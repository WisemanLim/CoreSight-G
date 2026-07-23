"""capacity-planner — 용량 계획·GPU 효율·비용 거버넌스 Addon Agent (PRD P2-4).

마운트 경로: /api/addon/capacity-planner/...
엔드포인트:
  GET  /tools              지원 도구 목록
  POST /tools/{tool_name}  도구 실행
  GET  /status             저활용 GPU 수 요약 (대시보드 위젯)

근거: ROI 보고서 보존 전략·비용 최적화, 시장 보고서 로드맵 5단계 "capacity planning·cost governance".
Domain Agent 연동 규약: `router` + `_TOOLS` + `TOOL_EXECUTORS` + `SYSTEM_PROMPT` export.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.services import prometheus
from app.services.prometheus import PrometheusError

router = APIRouter(tags=["capacity-planner"])

SYSTEM_PROMPT = (
    "당신은 CoreSight-G 플랫폼의 용량 계획·비용 효율 전문가입니다. "
    "제공된 도구로 Prometheus 에서 실제 장기 추세 데이터를 조회한 뒤 답변합니다. "
    "조회 없이 활용률을 추정하지 마세요. "
    "해석 기준: 평균 utilization 10% 이하 장기 지속 = 저활용(잡 재배치·스케일다운 검토 대상), "
    "90% 이상 장기 지속 = 과포화(증설 검토), 활성 시계열 수 급증 = 카디널리티·저장 비용 위험 신호. "
    "PRD 성공지표(TCO $0 라이선스, 운영시간 주 4h 이내, 15s~30s 수집주기 준수율 95%+)를 기준으로 "
    "비용 효율 판단을 제시하며, 조치 실행은 지원하지 않고 권고만 제시합니다."
)

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_underutilized_gpus",
        "description": "지정 기간 평균 utilization 이 임계값 이하인 저활용 GPU 목록을 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "hours": {"type": "integer", "description": "조회 기간(시간), 기본 24"},
                "threshold_percent": {"type": "number", "description": "저활용 판정 임계값(%), 기본 10"},
            },
        },
    },
    {
        "name": "get_efficiency_report",
        "description": "GPU 전체 평균 utilization/VRAM 사용률 및 노드별 요약을 조회합니다 (효율 리포트).",
        "input_schema": {
            "type": "object",
            "properties": {
                "hours": {"type": "integer", "description": "조회 기간(시간), 기본 24"},
            },
        },
    },
    {
        "name": "get_cardinality_summary",
        "description": "활성 시계열 수(카디널리티)를 메트릭 이름별로 조회합니다 (저장 비용 거버넌스).",
        "input_schema": {"type": "object", "properties": {}},
    },
]


async def _avg_over_range(promql: str, hours: int) -> list[dict[str, Any]]:
    """avg_over_time 랩핑 instant query — GPU/노드 단위 기간 평균."""
    return await prometheus.query(f"avg_over_time({promql}[{hours}h])")


async def _get_underutilized_gpus(tool_input: dict) -> dict:
    hours = int(tool_input.get("hours") or 24)
    threshold = float(tool_input.get("threshold_percent") or 10)
    try:
        samples = await _avg_over_range("DCGM_FI_DEV_GPU_UTIL", hours)
    except PrometheusError as exc:
        return {"error": str(exc)}
    under = [
        {
            "hostname": s["metric"].get("Hostname", "unknown"),
            "gpu": s["metric"].get("gpu", "?"),
            "avg_util_percent": round(float(s["value"][1]), 2),
        }
        for s in samples
        if float(s["value"][1]) <= threshold
    ]
    return {"hours": hours, "threshold_percent": threshold, "count": len(under), "gpus": under}


async def _get_efficiency_report(tool_input: dict) -> dict:
    hours = int(tool_input.get("hours") or 24)
    try:
        util_samples = await _avg_over_range("DCGM_FI_DEV_GPU_UTIL", hours)
        used_samples = await _avg_over_range("DCGM_FI_DEV_FB_USED", hours)
        total_samples = await prometheus.query("DCGM_FI_DEV_FB_TOTAL")
    except PrometheusError as exc:
        return {"error": str(exc)}

    total_by_gpu = {
        (s["metric"].get("Hostname", "?"), s["metric"].get("gpu", "?")): float(s["value"][1])
        for s in total_samples
    }
    used_by_gpu = {
        (s["metric"].get("Hostname", "?"), s["metric"].get("gpu", "?")): float(s["value"][1])
        for s in used_samples
    }

    rows = []
    for s in util_samples:
        key = (s["metric"].get("Hostname", "?"), s["metric"].get("gpu", "?"))
        total = total_by_gpu.get(key)
        used = used_by_gpu.get(key)
        vram_pct = round(used / total * 100, 1) if total and used is not None else None
        rows.append({
            "hostname": key[0], "gpu": key[1],
            "avg_util_percent": round(float(s["value"][1]), 2),
            "avg_vram_percent": vram_pct,
        })

    avg_util = round(sum(r["avg_util_percent"] for r in rows) / len(rows), 2) if rows else 0.0
    return {"hours": hours, "gpu_count": len(rows), "fleet_avg_util_percent": avg_util, "gpus": rows}


async def _get_cardinality_summary(tool_input: dict) -> dict:
    try:
        series = await prometheus.query('count({__name__=~"DCGM_FI_.+|hw_.+"}) by (__name__)')
    except PrometheusError as exc:
        return {"error": str(exc)}
    rows = sorted(
        ({"metric": s["metric"].get("__name__", "?"), "series": int(float(s["value"][1]))} for s in series),
        key=lambda r: -r["series"],
    )
    return {"total_series": sum(r["series"] for r in rows), "by_metric": rows}


TOOL_EXECUTORS: dict[str, Any] = {
    "get_underutilized_gpus": _get_underutilized_gpus,
    "get_efficiency_report": _get_efficiency_report,
    "get_cardinality_summary": _get_cardinality_summary,
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
        under = await _get_underutilized_gpus({"hours": 24, "threshold_percent": 10})
    except Exception:  # noqa: BLE001 — 위젯은 항상 응답
        under = {"count": 0}
    if "error" in under:
        raise HTTPException(status_code=503, detail=under["error"])
    return {"underutilized_gpus_24h": under.get("count", 0)}
