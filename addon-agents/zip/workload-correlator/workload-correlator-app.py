"""workload-correlator — 프로세스/잡별 GPU 점유 상관분석 Addon Agent (PRD P2-7).

마운트 경로: /api/addon/workload-correlator/...
엔드포인트:
  GET  /tools              지원 도구 목록
  POST /tools/{tool_name}  도구 실행
  GET  /status             활성 잡·GPU 점유 프로세스 수 요약 (대시보드 위젯)

근거: `.docs/gpu_server_monitoring_scale_guide.md` "GPU 노드/잡/파드 상관분석",
GPU 모니터링 목적 "프로세스별 원인 분석". 스케줄러 메타데이터(job_id/user)를
GPU 프로세스 메모리 점유와 연계해 "누가/어떤 잡이 어느 GPU 를 얼마나 쓰는지" 를 답한다.
Domain Agent 연동 규약: `router` + `_TOOLS` + `TOOL_EXECUTORS` + `SYSTEM_PROMPT` export.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.services import prometheus
from app.services.prometheus import PrometheusError

router = APIRouter(tags=["workload-correlator"])

SYSTEM_PROMPT = (
    "당신은 CoreSight-G 플랫폼의 워크로드-GPU 상관분석 전문가입니다. "
    "제공된 도구로 Prometheus 에서 실제 GPU 프로세스별 메모리 점유와 잡/사용자 메타데이터를 "
    "조회한 뒤 답변합니다. 조회 없이 점유량을 추정하지 마세요. "
    "해석 기준: 동일 job_id 가 여러 GPU 에 걸쳐 있으면 분산 학습 잡, 특정 사용자의 누적 점유가 "
    "비정상적으로 크면 과점유 후보, GPU 저활용(gpu_profiling/capacity_planning intent 참고)과 "
    "프로세스 부재가 겹치면 유휴 GPU 로 판단. "
    "조치 실행(프로세스 종료 등)은 지원하지 않으며 재배치 권고만 제시합니다."
)

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_gpu_process_map",
        "description": "GPU 별 활성 프로세스(pid, job_id, user, 메모리 점유)를 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_usage_by_job",
        "description": "job_id 단위로 집계한 GPU 메모리 점유 및 사용 GPU 목록을 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_usage_by_user",
        "description": "user 단위로 집계한 GPU 메모리 점유 및 사용 GPU 목록을 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


async def _process_map() -> list[dict[str, Any]]:
    """GPU 프로세스 원본 목록 (구현체 내 조회 로직 — Addon-first)."""
    rows = []
    for sample in await prometheus.query("DCGM_FI_DEV_GPU_PROCESS_MEM_USED"):
        m = sample["metric"]
        rows.append({
            "hostname": m.get("Hostname", "unknown"),
            "gpu": m.get("gpu", "?"),
            "pid": m.get("pid", "?"),
            "job_id": m.get("job_id", "unknown"),
            "user": m.get("user", "unknown"),
            "memory_used_mib": float(sample["value"][1]),
        })
    return sorted(rows, key=lambda r: (r["hostname"], r["gpu"]))


def _aggregate(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for r in rows:
        g = groups.setdefault(r[key], {key: r[key], "total_memory_mib": 0.0, "gpus": set(), "process_count": 0})
        g["total_memory_mib"] += r["memory_used_mib"]
        g["gpus"].add(r["gpu"])
        g["process_count"] += 1
    result = []
    for g in groups.values():
        g["gpus"] = sorted(g["gpus"])
        g["total_memory_mib"] = round(g["total_memory_mib"], 1)
        result.append(g)
    return sorted(result, key=lambda g: -g["total_memory_mib"])


async def _get_gpu_process_map(tool_input: dict) -> dict:
    try:
        return {"processes": await _process_map()}
    except PrometheusError as exc:
        return {"error": str(exc)}


async def _get_usage_by_job(tool_input: dict) -> dict:
    try:
        rows = await _process_map()
    except PrometheusError as exc:
        return {"error": str(exc)}
    return {"jobs": _aggregate(rows, "job_id")}


async def _get_usage_by_user(tool_input: dict) -> dict:
    try:
        rows = await _process_map()
    except PrometheusError as exc:
        return {"error": str(exc)}
    return {"users": _aggregate(rows, "user")}


TOOL_EXECUTORS: dict[str, Any] = {
    "get_gpu_process_map": _get_gpu_process_map,
    "get_usage_by_job": _get_usage_by_job,
    "get_usage_by_user": _get_usage_by_user,
}


# ─── REST 노출 (MCP/외부 연동·수동 점검용) ───────────────────────────────────

@router.get("/tools")
async def list_tools(user: dict = Depends(get_current_user)):
    return {"tools": _TOOLS}


@router.post("/tools/{tool_name}")
async def call_tool(tool_name: str, arguments: dict | None = None, user: dict = Depends(get_current_user)):
    executor = TOOL_EXECUTORS.get(tool_name)
    if executor is None:
        raise HTTPException(status_code=404, detail=f"알 수 없는 도구: {tool_name}")
    return {"result": await executor(arguments or {})}


@router.get("/status")
async def status(user: dict = Depends(get_current_user)):
    try:
        rows = await _process_map()
    except PrometheusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    jobs = {r["job_id"] for r in rows}
    return {"active_processes": len(rows), "active_jobs": len(jobs)}
