"""gpu-profiler — GPU 고급 프로파일링 지표 Addon Agent (PRD P2-3).

마운트 경로: /api/addon/gpu-profiler/...
엔드포인트:
  GET  /tools              지원 도구 목록
  POST /tools/{tool_name}  도구 실행
  GET  /status             throttle 중인 GPU 수 요약 (대시보드 위젯)

수집 우선순위 2·3순위 지표(SM occupancy, Tensor pipe active, DRAM bandwidth, throttle reasons,
PCIe throughput) — gpu-monitor(1순위 기본 운영 지표)와 분리해 카디널리티·비용을 통제한다.
Domain Agent 연동 규약: `router` + `_TOOLS` + `TOOL_EXECUTORS` + `SYSTEM_PROMPT` export.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.services import prometheus
from app.services.prometheus import PrometheusError

router = APIRouter(tags=["gpu-profiler"])

SYSTEM_PROMPT = (
    "당신은 CoreSight-G 플랫폼의 GPU 성능 프로파일링 전문가입니다. "
    "제공된 도구로 Prometheus 에서 실제 GPU 고급 지표(SM occupancy, Tensor pipe active, "
    "DRAM bandwidth, throttle, PCIe throughput)를 조회한 뒤 답변합니다. "
    "조회 없이 수치를 추정하지 마세요. "
    "해석 기준: SM occupancy 낮음+utilization 높음 = 커널 비효율(그리드 크기 재검토), "
    "Tensor pipe active 낮음 = 혼합정밀도 미활용 가능성, DRAM active 높음+SM occupancy 낮음 = "
    "메모리 바운드 워크로드, throttle_reasons>0 지속 = 전력/온도 제한(GPUOverTemperature·전력 확인), "
    "PCIe throughput 포화 = 호스트↔GPU 전송 병목(배치 크기·pinned memory 검토). "
    "조치 실행은 지원하지 않으며 튜닝 권고만 제시합니다."
)

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_gpu_profile",
        "description": "GPU 별 고급 프로파일링 지표(SM occupancy, Tensor pipe active, DRAM active, "
                        "throttle reasons, PCIe TX/RX)를 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_throttled_gpus",
        "description": "현재 클럭 throttle 이 걸린 GPU 목록을 조회합니다 (전력/온도 제한 탐지).",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "query_promql",
        "description": "PromQL instant query 를 직접 실행합니다 (세부·추세 조회용).",
        "input_schema": {
            "type": "object",
            "properties": {
                "promql": {"type": "string", "description": "실행할 PromQL 식"},
            },
            "required": ["promql"],
        },
    },
]

_PROFILE_METRICS = {
    "sm_occupancy": "DCGM_FI_PROF_SM_OCCUPANCY",
    "tensor_pipe_active": "DCGM_FI_PROF_PIPE_TENSOR_ACTIVE",
    "dram_active": "DCGM_FI_PROF_DRAM_ACTIVE",
    "throttle_reasons": "DCGM_FI_DEV_CLOCK_THROTTLE_REASONS",
    "pcie_tx_bytes": "DCGM_FI_PROF_PCIE_TX_BYTES",
    "pcie_rx_bytes": "DCGM_FI_PROF_PCIE_RX_BYTES",
}


async def _gpu_profile() -> list[dict[str, Any]]:
    """GPU 단위 고급 지표 병합 (구현체 내 조회 로직 — Addon-first)."""
    gpus: dict[tuple[str, str], dict[str, Any]] = {}
    for field, name in _PROFILE_METRICS.items():
        for sample in await prometheus.query(name):
            m = sample["metric"]
            key = (m.get("Hostname", "unknown"), m.get("gpu", "?"))
            entry = gpus.setdefault(key, {"hostname": key[0], "gpu": key[1]})
            entry[field] = float(sample["value"][1])
    return sorted(gpus.values(), key=lambda g: (g["hostname"], g["gpu"]))


async def _get_gpu_profile(tool_input: dict) -> dict:
    try:
        return {"gpus": await _gpu_profile()}
    except PrometheusError as exc:
        return {"error": str(exc)}


async def _get_throttled_gpus(tool_input: dict) -> dict:
    try:
        gpus = await _gpu_profile()
    except PrometheusError as exc:
        return {"error": str(exc)}
    throttled = [g for g in gpus if g.get("throttle_reasons", 0) > 0]
    return {"count": len(throttled), "gpus": throttled}


async def _query_promql(tool_input: dict) -> dict:
    try:
        return {"result": await prometheus.query(tool_input["promql"])}
    except PrometheusError as exc:
        return {"error": str(exc)}


TOOL_EXECUTORS: dict[str, Any] = {
    "get_gpu_profile": _get_gpu_profile,
    "get_throttled_gpus": _get_throttled_gpus,
    "query_promql": _query_promql,
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
        gpus = await _gpu_profile()
    except PrometheusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    throttled = sum(1 for g in gpus if g.get("throttle_reasons", 0) > 0)
    return {"gpu_count": len(gpus), "throttled": throttled}
