"""storage-monitor — 스토리지(디스크 latency/IOPS/SMART/NVMe/RAID) 진단 Addon Agent (PRD P2-1).

마운트 경로: /api/addon/storage-monitor/...
엔드포인트:
  GET  /tools              지원 도구 목록
  POST /tools/{tool_name}  도구 실행
  GET  /status             디스크 헬스 요약 (대시보드 위젯)

Domain Agent 연동 규약: `router` + `_TOOLS` + `TOOL_EXECUTORS` + `SYSTEM_PROMPT` export.
스냅샷 조회 로직은 core 가 아닌 이 구현체에 있다 (Addon-first 원칙, PRD §7).
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.services import prometheus
from app.services.prometheus import PrometheusError

router = APIRouter(tags=["storage-monitor"])

SYSTEM_PROMPT = (
    "당신은 CoreSight-G 플랫폼의 스토리지 진단 전문가입니다. "
    "제공된 도구로 Prometheus 에서 실제 디스크·RAID 지표를 조회한 뒤 답변합니다. "
    "조회 없이 수치를 추정하지 마세요. "
    "이상 징후 해석 기준: SMART unhealthy = 즉시 교체 검토·백업 확인, "
    "읽기 지연 50ms 이상 지속 = 스토리지 병목(워크로드/케이블/컨트롤러 점검), "
    "NVMe wear 80% 초과 = 수명 관리 대상, RAID degraded = 즉시 티켓 발행·rebuild 계획, "
    "IOPS 급락 = 큐 적체 또는 디바이스 이상. "
    "조치 실행은 지원하지 않으며 권고만 제시합니다."
)

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_storage_snapshot",
        "description": "디바이스 별 스토리지 상태(read/write latency, IOPS, SMART, NVMe wear)와 RAID 상태를 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_active_alerts",
        "description": "현재 활성(firing/pending) 알람 목록을 조회합니다 (SMART/latency/RAID 포함).",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "query_promql",
        "description": "PromQL instant query 를 직접 실행합니다 (특정 디바이스·추세 세부 조회용).",
        "input_schema": {
            "type": "object",
            "properties": {
                "promql": {"type": "string", "description": "실행할 PromQL 식"},
            },
            "required": ["promql"],
        },
    },
]

_DEVICE_METRICS = {
    "read_latency_ms": "hw_disk_read_latency_ms",
    "write_latency_ms": "hw_disk_write_latency_ms",
    "smart_healthy": "hw_smart_healthy",
    "nvme_wear_percent": "hw_nvme_wear_level_percent",
}


async def _storage_snapshot() -> dict:
    """디바이스 단위 병합 스냅샷 + RAID 상태 (구현체 내 조회 로직 — Addon-first)."""
    devices: dict[tuple[str, str], dict[str, Any]] = {}
    for field, name in _DEVICE_METRICS.items():
        for sample in await prometheus.query(name):
            m = sample["metric"]
            key = (m.get("Hostname", "unknown"), m.get("device", "?"))
            entry = devices.setdefault(key, {"hostname": key[0], "device": key[1]})
            entry[field] = float(sample["value"][1])
    for sample in await prometheus.query("hw_disk_iops"):
        m = sample["metric"]
        key = (m.get("Hostname", "unknown"), m.get("device", "?"))
        entry = devices.setdefault(key, {"hostname": key[0], "device": key[1]})
        entry[f"iops_{m.get('op', 'unknown')}"] = float(sample["value"][1])
    raid = [
        {"hostname": s["metric"].get("Hostname", "unknown"),
         "controller": s["metric"].get("controller", "?"),
         "degraded": float(s["value"][1]) > 0}
        for s in await prometheus.query("hw_raid_degraded")
    ]
    return {
        "devices": sorted(devices.values(), key=lambda d: (d["hostname"], d["device"])),
        "raid": raid,
    }


async def _get_storage_snapshot(tool_input: dict) -> dict:
    try:
        return await _storage_snapshot()
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
    "get_storage_snapshot": _get_storage_snapshot,
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
    """대시보드 위젯 — 디스크·RAID 헬스 요약."""
    try:
        snap = await _storage_snapshot()
    except PrometheusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    devices = snap["devices"]
    unhealthy = [d for d in devices if d.get("smart_healthy") == 0.0]
    raid_degraded = sum(1 for r in snap["raid"] if r["degraded"])
    return {
        "device_count": len(devices),
        "smart_unhealthy": len(unhealthy),
        "raid_degraded": raid_degraded,
    }
