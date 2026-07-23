"""Phase 18 — 알림 채널(Alertmanager webhook) 시험."""
import os
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")

_PAYLOAD = {
    "status": "firing",
    "alerts": [
        {
            "status": "firing",
            "labels": {
                "alertname": "GPUXidError",
                "severity": "critical",
                "layer": "gpu",
                "Hostname": "gpu-node-01",
                "gpu": "3",
            },
            "annotations": {"summary": "GPU 3@gpu-node-01 XID 오류 발생"},
            "startsAt": "2026-07-22T08:00:00Z",
            "endsAt": "0001-01-01T00:00:00Z",
        }
    ],
}


@pytest.fixture
def client():
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


def _auth():
    from app.core.config import settings
    return {"Authorization": f"Bearer {settings.alert_webhook_token}"}


# ── TC-18-01: 토큰 검증 ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_webhook_rejects_bad_token(client):
    async with client as c:
        r1 = await c.post("/api/alerts/webhook", json=_PAYLOAD)
        r2 = await c.post("/api/alerts/webhook", json=_PAYLOAD,
                          headers={"Authorization": "Bearer wrong"})
    assert r1.status_code == 401 and r2.status_code == 401


# ── TC-18-02: 수신·저장 ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_webhook_stores_alerts(client):
    inserted = []

    async def fake_insert(sql, params=()):
        inserted.append(params)
        return 1

    with patch("app.routers.router_alerts.execute_insert", new=AsyncMock(side_effect=fake_insert)):
        async with client as c:
            resp = await c.post("/api/alerts/webhook", json=_PAYLOAD, headers=_auth())

    assert resp.status_code == 200 and resp.json()["stored"] == 1
    assert inserted[0][0] == "GPUXidError" and inserted[0][3] == "gpu-node-01"


# ── TC-18-03/04: 외부 중계 (_forward_external 직접 시험 — ASGI 클라이언트 오염 방지) ──

@pytest.mark.asyncio
async def test_forward_external_when_configured():
    from unittest.mock import MagicMock

    from app.core.config import settings
    from app.routers.router_alerts import _forward_external

    post_mock = AsyncMock()
    fake_client = MagicMock()
    fake_client.__aenter__ = AsyncMock(return_value=MagicMock(post=post_mock))
    fake_client.__aexit__ = AsyncMock(return_value=False)

    with (
        patch.object(settings, "notify_webhook_url", "http://notify.example/hook"),
        patch("app.routers.router_alerts.httpx.AsyncClient", return_value=fake_client),
    ):
        await _forward_external(_PAYLOAD)
    assert post_mock.await_count == 1
    assert post_mock.await_args.args[0] == "http://notify.example/hook"


@pytest.mark.asyncio
async def test_forward_failure_swallowed():
    from app.core.config import settings
    from app.routers.router_alerts import _forward_external

    with (
        patch.object(settings, "notify_webhook_url", "http://notify.example/hook"),
        patch("app.routers.router_alerts.httpx.AsyncClient", side_effect=RuntimeError("down")),
    ):
        await _forward_external(_PAYLOAD)  # 예외 전파 없어야 함


# ── TC-18-05/06: history ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_history_requires_auth(client):
    async with client as c:
        resp = await c.get("/api/alerts/history")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_history_returns_rows(client):
    from app.main import app
    from app.core.deps import get_current_user

    rows = [{"id": 2, "alertname": "GPUXidError", "status": "firing"}]
    app.dependency_overrides[get_current_user] = lambda: {"user_id": "t", "role": "admin"}
    try:
        with patch("app.routers.router_alerts.fetch_all", new=AsyncMock(return_value=rows)):
            async with client as c:
                resp = await c.get("/api/alerts/history", params={"limit": 10})
        assert resp.status_code == 200
        assert resp.json()["alerts"][0]["alertname"] == "GPUXidError"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
