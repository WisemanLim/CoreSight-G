"""Phase 15 — 통합 대시보드 백엔드(gpu/history) 시험."""
import os
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")


# ── TC-15-01: gpu_util_history 변환 ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_gpu_util_history_transforms_series():
    from app.services import prometheus as svc

    raw = [
        {
            "metric": {"Hostname": "gpu-node-01", "gpu": "1"},
            "values": [["1700000000", "50.0"], ["1700000060", "75.5"]],
        },
        {
            "metric": {"Hostname": "gpu-node-01", "gpu": "0"},
            "values": [["1700000000", "10.0"]],
        },
    ]
    with patch.object(svc, "query_range", new=AsyncMock(return_value=raw)):
        series = await svc.gpu_util_history(30, 60)

    assert [s["gpu"] for s in series] == ["0", "1"]  # 정렬
    assert series[1]["points"] == [[1700000000.0, 50.0], [1700000060.0, 75.5]]
    assert series[1]["hostname"] == "gpu-node-01"


# ── TC-15-02/03/04: history 엔드포인트 ──────────────────────────────────────

@pytest.fixture
def client():
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_history_requires_auth(client):
    async with client as c:
        resp = await c.get("/api/metrics/gpu/history")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_history_ok_with_auth_override(client):
    from app.main import app
    from app.core.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: {"user_id": "t", "role": "admin"}
    try:
        with patch(
            "app.routers.router_metrics.prometheus.gpu_util_history",
            new=AsyncMock(return_value=[{"hostname": "n1", "gpu": "0", "points": [[1, 2.0]]}]),
        ):
            async with client as c:
                resp = await c.get("/api/metrics/gpu/history", params={"minutes": 30, "step": 60})
        assert resp.status_code == 200
        assert resp.json()["series"][0]["points"] == [[1, 2.0]]
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_history_validates_params(client):
    from app.main import app
    from app.core.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: {"user_id": "t", "role": "admin"}
    try:
        async with client as c:
            resp = await c.get("/api/metrics/gpu/history", params={"minutes": 0})
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.pop(get_current_user, None)
