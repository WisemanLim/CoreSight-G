"""anomaly-detector — 메트릭 이상 탐지·원인 분석 보조 Addon Agent (PRD P2-5).

마운트 경로: /api/addon/anomaly-detector/...
엔드포인트:
  GET  /tools              지원 도구 목록
  POST /tools/{tool_name}  도구 실행
  GET  /status             현재 이상 탐지 건수 요약 (대시보드 위젯)

방식: 통계 기반(z-score) — 별도 ML 인프라 없이 range query 표준편차로 이상치 탐지.
근거: 시장 보고서 "AI/ML 이상 탐지·예측 = 핵심 차별점", "알람 노이즈 감소".
Domain Agent 연동 규약: `router` + `_TOOLS` + `TOOL_EXECUTORS` + `SYSTEM_PROMPT` export.
"""
import statistics
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.services import prometheus
from app.services.prometheus import PrometheusError

router = APIRouter(tags=["anomaly-detector"])

SYSTEM_PROMPT = (
    "당신은 CoreSight-G 플랫폼의 이상 탐지·원인 분석 보조 전문가입니다. "
    "제공된 도구로 실제 메트릭 시계열의 통계적 이상치(z-score)와 활성 알람을 조회한 뒤 답변합니다. "
    "조회 없이 이상 여부를 추정하지 마세요. "
    "해석 기준: |z-score| 3 이상 = 통계적 이상치(추세 급변), 이상 탐지와 활성 알람이 같은 노드/GPU 에 "
    "동시 발생하면 상관관계로 보고 근본 원인 후보로 제시, 단발성 이상은 노이즈일 수 있으므로 "
    "지속 여부를 함께 확인하도록 권고합니다. z-score 는 통계적 신호일 뿐 확정 진단이 아님을 명시하고, "
    "조치 실행은 지원하지 않으며 조사 우선순위만 제시합니다."
)

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "detect_metric_anomalies",
        "description": "지정 PromQL 시계열에서 z-score 기반 통계적 이상치를 탐지합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "promql": {"type": "string", "description": "조회할 메트릭 (예: DCGM_FI_DEV_GPU_UTIL)"},
                "hours": {"type": "integer", "description": "조회 기간(시간), 기본 6"},
                "z_threshold": {"type": "number", "description": "이상 판정 z-score 임계값, 기본 3.0"},
            },
            "required": ["promql"],
        },
    },
    {
        "name": "correlate_alerts",
        "description": "현재 활성 알람들을 노드/GPU 단위로 그룹핑해 동시 발생(상관) 패턴을 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


def _zscores(values: list[float]) -> list[float]:
    if len(values) < 2:
        return [0.0] * len(values)
    mean = statistics.mean(values)
    stdev = statistics.pstdev(values)
    if stdev == 0:
        return [0.0] * len(values)
    return [(v - mean) / stdev for v in values]


async def _detect_metric_anomalies(tool_input: dict) -> dict:
    promql = tool_input.get("promql")
    if not promql:
        return {"error": "promql 필수"}
    hours = int(tool_input.get("hours") or 6)
    z_threshold = float(tool_input.get("z_threshold") or 3.0)
    try:
        series = await prometheus.query_range(promql, minutes=hours * 60, step_seconds=60)
    except PrometheusError as exc:
        return {"error": str(exc)}

    anomalies = []
    for s in series:
        values = [float(v) for _, v in s["values"]]
        if len(values) < 5:
            continue
        zs = _zscores(values)
        for (ts, raw), z in zip(s["values"], zs):
            if abs(z) >= z_threshold:
                anomalies.append({
                    "labels": s["metric"],
                    "timestamp": float(ts),
                    "value": float(raw),
                    "z_score": round(z, 2),
                })
    anomalies.sort(key=lambda a: -abs(a["z_score"]))
    return {"promql": promql, "hours": hours, "z_threshold": z_threshold, "count": len(anomalies),
            "anomalies": anomalies[:50]}


async def _correlate_alerts(tool_input: dict) -> dict:
    try:
        alerts = await prometheus.active_alerts()
    except PrometheusError as exc:
        return {"error": str(exc)}
    groups: dict[str, list[dict]] = {}
    for a in alerts:
        labels = a.get("labels", {})
        key = labels.get("Hostname") or labels.get("gpu") or "unknown"
        groups.setdefault(key, []).append({
            "alertname": labels.get("alertname"),
            "severity": labels.get("severity"),
            "state": a.get("state"),
        })
    correlated = {k: v for k, v in groups.items() if len(v) >= 2}
    return {"total_active": len(alerts), "correlated_targets": len(correlated), "groups": correlated}


TOOL_EXECUTORS: dict[str, Any] = {
    "detect_metric_anomalies": _detect_metric_anomalies,
    "correlate_alerts": _correlate_alerts,
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
        corr = await _correlate_alerts({})
    except Exception:  # noqa: BLE001 — 위젯은 항상 응답
        corr = {"correlated_targets": 0}
    if "error" in corr:
        raise HTTPException(status_code=503, detail=corr["error"])
    return {"correlated_targets": corr.get("correlated_targets", 0)}
