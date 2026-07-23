"""hw-monitor — 서버 하드웨어(CPU/메모리/RAID/PSU/센서) 관제 Addon Agent.

마운트 경로: /api/addon/hw-monitor/...
엔드포인트:
  GET  /tools              지원 도구 목록
  POST /tools/{tool_name}  도구 실행
  GET  /status             노드 헬스 요약

Domain Agent 연동 규약: `router` + `_TOOLS` + `TOOL_EXECUTORS` export —
core 의 AddonToolAgent 가 이 모듈에서 tool 정의·실행기를 읽어 tool_use 루프에 사용한다.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.services import prometheus
from app.services.prometheus import PrometheusError

router = APIRouter(tags=["hw-monitor"])

SYSTEM_PROMPT = (
    "당신은 CoreSight-G 플랫폼의 서버 하드웨어 모니터링 전문가입니다. "
    "제공된 도구로 Prometheus 에서 실제 하드웨어 메트릭·알람을 조회한 뒤 답변합니다. "
    "조회 없이 수치를 추정하지 마세요. "
    "이상 징후 해석 기준: RAID degraded = 즉시 티켓 발행 권고, PSU 장애 = 전원 이중화 점검, "
    "CPU 80% 장기 지속 = 용량 계획 검토, 흡기 온도 급상승 = 냉각 점검. "
    "조치 실행은 지원하지 않으며 권고만 제시합니다."
)

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_hardware_snapshot",
        "description": "노드 별 서버 하드웨어 상태(CPU, 메모리, RAID, PSU, 온도)를 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_active_alerts",
        "description": "현재 활성(firing/pending) 알람 목록을 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "query_promql",
        "description": "PromQL instant query 를 직접 실행합니다 (세부 센서·디스크 조회용).",
        "input_schema": {
            "type": "object",
            "properties": {
                "promql": {"type": "string", "description": "실행할 PromQL 식"},
            },
            "required": ["promql"],
        },
    },
]


async def _get_hardware_snapshot(tool_input: dict) -> dict:
    try:
        return {"nodes": await prometheus.hardware_snapshot()}
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
    "get_hardware_snapshot": _get_hardware_snapshot,
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
        nodes = await prometheus.hardware_snapshot()
    except PrometheusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    faulty = [n for n in nodes if (n.get("raid_degraded") or 0) > 0 or (n.get("psu_failed") or 0) > 0]
    return {"node_count": len(nodes), "faulty": len(faulty), "healthy": len(nodes) - len(faulty)}
