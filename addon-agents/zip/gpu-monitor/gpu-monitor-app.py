"""gpu-monitor — GPU 계층(utilization/VRAM/온도/전력/XID/ECC) 관제 Addon Agent.

마운트 경로: /api/addon/gpu-monitor/...
엔드포인트:
  GET  /tools              지원 도구 목록
  POST /tools/{tool_name}  도구 실행
  GET  /status             GPU 요약 헬스

Domain Agent 연동 규약: `router` + `_TOOLS` + `TOOL_EXECUTORS` export —
core 의 AddonToolAgent 가 이 모듈에서 tool 정의·실행기를 읽어 tool_use 루프에 사용한다.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.services import prometheus
from app.services.prometheus import PrometheusError

router = APIRouter(tags=["gpu-monitor"])

SYSTEM_PROMPT = (
    "당신은 CoreSight-G 플랫폼의 GPU 모니터링 전문가입니다. "
    "제공된 도구로 Prometheus 에서 실제 GPU 메트릭·알람을 조회한 뒤 답변합니다. "
    "조회 없이 수치를 추정하지 마세요. "
    "이상 징후 해석 기준: XID>0 = 즉시 조사 대상, ECC double-bit 증가 = 하드웨어 불안정, "
    "온도 85°C 초과 = 과열, VRAM 90% 이상 지속 = 메모리 병목, "
    "utilization 10% 이하 장기 지속 = 저활용. "
    "조치 실행(노드 격리·재시작)은 지원하지 않으며 권고만 제시합니다."
)

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_gpu_snapshot",
        "description": "전체 GPU 의 현재 상태(utilization, VRAM, 온도, 전력, XID, ECC)를 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_active_alerts",
        "description": "현재 활성(firing/pending) 알람 목록을 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "query_promql",
        "description": "PromQL instant query 를 직접 실행합니다 (추세·필터 등 세부 조회용).",
        "input_schema": {
            "type": "object",
            "properties": {
                "promql": {"type": "string", "description": "실행할 PromQL 식"},
            },
            "required": ["promql"],
        },
    },
]


async def _get_gpu_snapshot(tool_input: dict) -> dict:
    try:
        return {"gpus": await prometheus.gpu_snapshot()}
    except PrometheusError as exc:
        return {"error": str(exc)}


async def _get_active_alerts(tool_input: dict) -> dict:
    try:
        return {"alerts": await prometheus.active_alerts()}
    except PrometheusError as exc:
        return {"error": str(exc)}


async def _query_promql(tool_input: dict) -> dict:
    try:
        return {"result": await prometheus.query(tool_input["promql"])}
    except PrometheusError as exc:
        return {"error": str(exc)}


TOOL_EXECUTORS: dict[str, Any] = {
    "get_gpu_snapshot": _get_gpu_snapshot,
    "get_active_alerts": _get_active_alerts,
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
        gpus = await prometheus.gpu_snapshot()
    except PrometheusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    faulty = [g for g in gpus if (g.get("xid_errors") or 0) > 0 or (g.get("ecc_dbe_total") or 0) > 0]
    return {"gpu_count": len(gpus), "faulty": len(faulty), "healthy": len(gpus) - len(faulty)}
