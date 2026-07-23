"""알림 채널 — Alertmanager webhook 수신·이력 저장·외부 중계 (PRD §3 P0).

흐름: Prometheus 규칙 발화 → Alertmanager(그룹핑·중복제거) → POST /api/alerts/webhook
      → tbl_alert_history 저장 → notify_webhook_url 설정 시 외부 채널로 중계.
"""
import json
import logging

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.core.config import settings
from app.core.deps import get_current_user
from app.db import _PH, execute_insert, fetch_all

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


async def _forward_external(payload: dict) -> None:
    """notify_webhook_url 설정 시 외부 채널로 알람 중계 (실패해도 수신 처리는 유지)."""
    if not settings.notify_webhook_url:
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(settings.notify_webhook_url, json=payload)
    except Exception as exc:  # noqa: BLE001
        logger.warning("[alerts] 외부 채널 중계 실패: %s", exc)


@router.post("/webhook")
async def alertmanager_webhook(payload: dict, authorization: str = Header(default="")):
    """Alertmanager webhook 수신 — Bearer 토큰 검증 후 알람 이력 저장."""
    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.alert_webhook_token:
        raise HTTPException(status_code=401, detail="invalid webhook token")

    alerts = payload.get("alerts", [])
    stored = 0
    for a in alerts:
        labels = a.get("labels", {})
        await execute_insert(
            f"INSERT INTO tbl_alert_history "
            f"(alertname, severity, layer, hostname, gpu, status, summary, starts_at, ends_at, payload) "
            f"VALUES ({_PH}, {_PH}, {_PH}, {_PH}, {_PH}, {_PH}, {_PH}, {_PH}, {_PH}, {_PH})",
            (
                labels.get("alertname", "unknown"),
                labels.get("severity"),
                labels.get("layer"),
                labels.get("Hostname"),
                labels.get("gpu"),
                a.get("status", "unknown"),
                a.get("annotations", {}).get("summary"),
                a.get("startsAt"),
                a.get("endsAt"),
                json.dumps(a, ensure_ascii=False),
            ),
        )
        stored += 1
    logger.info("[alerts] webhook 수신: %d건 (%s)", stored, payload.get("status"))
    await _forward_external(payload)
    return {"stored": stored}


@router.get("/history")
async def alert_history(
    limit: int = Query(50, ge=1, le=500),
    user: dict = Depends(get_current_user),
):
    """알람 수신 이력 조회 (최신순)."""
    rows = await fetch_all(
        f"SELECT id, alertname, severity, layer, hostname, gpu, status, summary, "
        f"starts_at, ends_at, received_at FROM tbl_alert_history "
        f"ORDER BY id DESC LIMIT {_PH}",
        (limit,),
    )
    return {"alerts": rows}
