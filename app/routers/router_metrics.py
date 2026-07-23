"""메트릭 조회 API — GPU/HW 스냅샷·활성 알람·PromQL (PRD §3 P0).

읽기 전용(read-only). 조치 실행(노드 격리 등)은 PRD Out of Scope.
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.deps import get_current_user
from app.services import prometheus
from app.services.prometheus import PrometheusError

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/gpu")
async def gpu_metrics(user: dict = Depends(get_current_user)):
    """GPU 별 핵심 지표 스냅샷 (utilization/VRAM/온도/전력/XID/ECC)."""
    try:
        return {"gpus": await prometheus.gpu_snapshot()}
    except PrometheusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/gpu/history")
async def gpu_history(
    minutes: int = Query(30, ge=1, le=1440),
    step: int = Query(60, ge=15, le=3600),
    user: dict = Depends(get_current_user),
):
    """GPU utilization 시계열 (대시보드 스파크라인용)."""
    try:
        return {"series": await prometheus.gpu_util_history(minutes, step)}
    except PrometheusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/hardware")
async def hardware_metrics(user: dict = Depends(get_current_user)):
    """노드 별 서버 하드웨어 지표 스냅샷 (CPU/메모리/RAID/PSU/온도)."""
    try:
        return {"nodes": await prometheus.hardware_snapshot()}
    except PrometheusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/alerts")
async def alerts(user: dict = Depends(get_current_user)):
    """현재 활성(firing/pending) 알람 목록."""
    try:
        return {"alerts": await prometheus.active_alerts()}
    except PrometheusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/query")
async def promql_query(
    q: str = Query(..., description="PromQL instant query"),
    user: dict = Depends(get_current_user),
):
    """PromQL 직접 조회 (읽기 전용 instant query)."""
    try:
        return {"result": await prometheus.query(q)}
    except PrometheusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
