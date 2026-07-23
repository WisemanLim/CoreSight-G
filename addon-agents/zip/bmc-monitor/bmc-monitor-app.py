"""bmc-monitor — BMC/IPMI 센서·이벤트 관제 Addon Agent (PRD P2-2).

마운트 경로: /api/addon/bmc-monitor/...
엔드포인트:
  GET  /tools              지원 도구 목록
  POST /tools/{tool_name}  도구 실행
  GET  /status             센서·이벤트 헬스 요약 (대시보드 위젯)

데이터 소스 결합: 센서(팬·PSU·전압·온도·전력) = Prometheus, 이벤트 로그 = Loki(job=bmc).
Domain Agent 연동 규약: `router` + `_TOOLS` + `TOOL_EXECUTORS` + `SYSTEM_PROMPT` export.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.services import loki, prometheus
from app.services.loki import LokiError
from app.services.prometheus import PrometheusError

router = APIRouter(tags=["bmc-monitor"])

SYSTEM_PROMPT = (
    "당신은 CoreSight-G 플랫폼의 BMC/IPMI 하드웨어 관리 전문가입니다. "
    "제공된 도구로 실제 BMC 센서(Prometheus)와 BMC 이벤트 로그(Loki)를 조회한 뒤 답변합니다. "
    "조회 없이 상태를 추정하지 마세요. "
    "이상 징후 해석 기준: 팬 1000 RPM 미만 = 냉각 점검(과열 연쇄 위험), "
    "12V 레일 11.4V 미만/12.6V 초과 = 전원 계통 이상, PSU status 0 = 전원 이중화 점검, "
    "흡기 온도 급상승 = 랙 냉각 점검, BMC critical 이벤트 = 선제 티켓 발행 권고. "
    "조치 실행은 지원하지 않으며 권고만 제시합니다."
)

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_bmc_sensors",
        "description": "노드 별 BMC 센서 상태(팬 RPM, 전압 레일, PSU, 흡기 온도, 섀시 전력)를 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_bmc_events",
        "description": "BMC/iDRAC/iLO 이벤트 로그를 조회합니다 (Loki job=bmc). keyword·level·minutes 지정 가능.",
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "포함 키워드 (대소문자 무시)"},
                "level": {"type": "string", "enum": ["info", "warning", "error"]},
                "minutes": {"type": "integer", "description": "조회 범위(분), 기본 60"},
            },
        },
    },
    {
        "name": "get_active_alerts",
        "description": "현재 활성(firing/pending) 알람 목록을 조회합니다 (FanSpeedLow·VoltageOutOfRange·PSUFailure 포함).",
        "input_schema": {"type": "object", "properties": {}},
    },
]

_SENSOR_QUERIES = {
    "fans": "hw_fan_speed_rpm",
    "voltages": "hw_voltage_volts",
    "psu": "hw_psu_status",
    "inlet_temp_celsius": "hw_inlet_temp_celsius",
    "chassis_power_watts": "hw_bmc_power_watts",
}


async def _bmc_sensors() -> dict:
    """노드 단위 센서 병합 (구현체 내 조회 로직 — Addon-first)."""
    nodes: dict[str, dict[str, Any]] = {}

    def node_of(m: dict) -> dict:
        host = m.get("Hostname", "unknown")
        return nodes.setdefault(host, {"hostname": host, "fans": {}, "voltages": {}, "psu": {}})

    for sample in await prometheus.query(_SENSOR_QUERIES["fans"]):
        node_of(sample["metric"])["fans"][sample["metric"].get("fan", "?")] = float(sample["value"][1])
    for sample in await prometheus.query(_SENSOR_QUERIES["voltages"]):
        node_of(sample["metric"])["voltages"][sample["metric"].get("rail", "?")] = float(sample["value"][1])
    for sample in await prometheus.query(_SENSOR_QUERIES["psu"]):
        node_of(sample["metric"])["psu"][sample["metric"].get("psu", "?")] = float(sample["value"][1])
    for field in ("inlet_temp_celsius", "chassis_power_watts"):
        for sample in await prometheus.query(_SENSOR_QUERIES[field]):
            node_of(sample["metric"])[field] = float(sample["value"][1])
    return {"nodes": sorted(nodes.values(), key=lambda n: n["hostname"])}


async def _get_bmc_sensors(tool_input: dict) -> dict:
    try:
        return await _bmc_sensors()
    except PrometheusError as exc:
        return {"error": str(exc)}


async def _get_bmc_events(tool_input: dict) -> dict:
    logql = loki.build_logql(
        job="bmc",
        keyword=tool_input.get("keyword"),
        level=tool_input.get("level"),
    )
    try:
        entries = await loki.search(logql, minutes=int(tool_input.get("minutes") or 60), limit=50)
        return {"query": logql, "count": len(entries), "events": entries}
    except LokiError as exc:
        return {"error": str(exc)}


async def _get_active_alerts(tool_input: dict) -> dict:
    try:
        return {"alerts": await prometheus.active_alerts()}
    except PrometheusError as exc:
        return {"error": str(exc)}


TOOL_EXECUTORS: dict[str, Any] = {
    "get_bmc_sensors": _get_bmc_sensors,
    "get_bmc_events": _get_bmc_events,
    "get_active_alerts": _get_active_alerts,
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
    """대시보드 위젯 — 센서 이상·최근 error 이벤트 요약."""
    try:
        sensors = await _bmc_sensors()
    except PrometheusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    abnormal = 0
    for n in sensors["nodes"]:
        abnormal += sum(1 for rpm in n["fans"].values() if rpm < 1000)
        abnormal += sum(1 for v in n["psu"].values() if v == 0.0)
        v12 = n["voltages"].get("12V")
        if v12 is not None and not (11.4 <= v12 <= 12.6):
            abnormal += 1
    try:
        events = await loki.search(loki.build_logql(job="bmc", level="error"), minutes=60, limit=50)
        error_events_1h = len(events)
    except LokiError:
        error_events_1h = -1  # Loki 미가용 — 위젯은 센서 요약만 유효
    return {
        "node_count": len(sensors["nodes"]),
        "sensor_abnormal": abnormal,
        "error_events_1h": error_events_1h,
    }
