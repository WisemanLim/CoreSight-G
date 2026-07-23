"""net-monitor — 네트워크 인터페이스(NIC) 관제 Addon Agent (PRD P2-6).

마운트 경로: /api/addon/net-monitor/...
엔드포인트:
  GET  /tools              지원 도구 목록
  POST /tools/{tool_name}  도구 실행
  GET  /status             인터페이스 이상 요약 (대시보드 위젯)

근거: `.docs/gpu_server_monitoring_scale_guide.md` 체크리스트 "NIC error/drop 필수".
Domain Agent 연동 규약: `router` + `_TOOLS` + `TOOL_EXECUTORS` + `SYSTEM_PROMPT` export.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.services import prometheus
from app.services.prometheus import PrometheusError

router = APIRouter(tags=["net-monitor"])

SYSTEM_PROMPT = (
    "당신은 CoreSight-G 플랫폼의 네트워크 인터페이스 관제 전문가입니다. "
    "제공된 도구로 Prometheus 에서 실제 NIC 오류/드롭/처리량/링크 상태를 조회한 뒤 답변합니다. "
    "조회 없이 상태를 추정하지 마세요. "
    "이상 징후 해석 기준: 오류/드롭 카운터 증가 = 케이블·포트·드라이버 점검, "
    "링크 다운 = 즉시 물리 연결·스위치 포트 확인, 처리량 포화(대역폭 근접 지속) = 네트워크 병목. "
    "조치 실행은 지원하지 않으며 권고만 제시합니다."
)

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_nic_snapshot",
        "description": "인터페이스 별 오류/드롭 카운터, 링크 상태, RX/TX 처리량을 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_active_alerts",
        "description": "현재 활성(firing/pending) 알람 목록을 조회합니다 (NICErrorsIncreasing·NICLinkDown 포함).",
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

_NIC_METRICS = {
    "errors_total": "hw_nic_errors_total",
    "drops_total": "hw_nic_drops_total",
    "link_up": "hw_nic_link_up",
    "rx_bytes_per_sec": "hw_nic_rx_bytes_per_sec",
    "tx_bytes_per_sec": "hw_nic_tx_bytes_per_sec",
}


async def _nic_snapshot() -> list[dict[str, Any]]:
    """인터페이스 단위 병합 스냅샷 (구현체 내 조회 로직 — Addon-first)."""
    nics: dict[tuple[str, str], dict[str, Any]] = {}
    for field, name in _NIC_METRICS.items():
        for sample in await prometheus.query(name):
            m = sample["metric"]
            key = (m.get("Hostname", "unknown"), m.get("nic", "?"))
            entry = nics.setdefault(key, {"hostname": key[0], "nic": key[1]})
            entry[field] = float(sample["value"][1])
    return sorted(nics.values(), key=lambda n: (n["hostname"], n["nic"]))


async def _get_nic_snapshot(tool_input: dict) -> dict:
    try:
        return {"interfaces": await _nic_snapshot()}
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
    "get_nic_snapshot": _get_nic_snapshot,
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
        interfaces = await _nic_snapshot()
    except PrometheusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    link_down = sum(1 for n in interfaces if n.get("link_up") == 0.0)
    with_errors = sum(1 for n in interfaces if (n.get("errors_total") or 0) > 0)
    return {"interface_count": len(interfaces), "link_down": link_down, "with_errors": with_errors}
