"""Phase 14 — GPU/HW 메트릭 수집 계층 + 관제 Domain Agent 시험."""
import os
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")


def _sample(name: str, value: float, **labels) -> dict:
    return {"metric": {"__name__": name, **labels}, "value": [0, str(value)]}


# ── TC-14-01: gpu_snapshot 병합 ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_gpu_snapshot_merges_metrics_per_gpu():
    from app.services import prometheus as svc

    async def fake_query(promql: str):
        lbl = {"Hostname": "gpu-node-01", "gpu": "0"}
        table = {
            "DCGM_FI_DEV_GPU_UTIL": 90.0,
            "DCGM_FI_DEV_FB_USED": 40960.0,
            "DCGM_FI_DEV_FB_TOTAL": 81920.0,
            "DCGM_FI_DEV_GPU_TEMP": 65.0,
            "DCGM_FI_DEV_POWER_USAGE": 300.0,
            "DCGM_FI_DEV_XID_ERRORS": 0.0,
            "DCGM_FI_DEV_ECC_DBE_VOL_TOTAL": 0.0,
        }
        return [_sample(promql, table[promql], **lbl)] if promql in table else []

    with patch.object(svc, "query", new=AsyncMock(side_effect=fake_query)):
        gpus = await svc.gpu_snapshot()

    assert len(gpus) == 1
    g = gpus[0]
    assert g["hostname"] == "gpu-node-01" and g["gpu"] == "0"
    assert g["util_percent"] == 90.0
    assert g["vram_used_percent"] == 50.0  # 40960/81920


# ── TC-14-02: hardware_snapshot 필터·기본값 ─────────────────────────────────

@pytest.mark.asyncio
async def test_hardware_snapshot_filters_and_defaults():
    from app.services import prometheus as svc

    async def fake_query(promql: str):
        if promql == "hw_cpu_usage_percent":
            return [
                _sample("hw_cpu_usage_percent", 30.0, Hostname="gpu-node-01"),
                _sample("hw_cpu_usage_percent", 99.0),  # Hostname 없음 → 제외 대상
            ]
        return []

    with patch.object(svc, "query", new=AsyncMock(side_effect=fake_query)):
        nodes = await svc.hardware_snapshot()

    assert len(nodes) == 1
    assert nodes[0]["hostname"] == "gpu-node-01"
    assert nodes[0]["psu_failed"] == 0.0  # 결측 보정


# ── TC-14-03: 연결 실패 → PrometheusError ───────────────────────────────────

@pytest.mark.asyncio
async def test_query_raises_on_connection_error():
    import httpx
    from app.services import prometheus as svc

    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=httpx.ConnectError("boom"))):
        with pytest.raises(svc.PrometheusError):
            await svc.query("up")


# ── TC-14-04/05/06: 메트릭 API ──────────────────────────────────────────────

@pytest.fixture
def client():
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_metrics_endpoints_require_auth(client):
    async with client as c:
        for path in ("/api/metrics/gpu", "/api/metrics/hardware", "/api/metrics/alerts"):
            resp = await c.get(path)
            assert resp.status_code in (401, 403), path


@pytest.mark.asyncio
async def test_metrics_gpu_ok_with_auth_override(client):
    from app.main import app
    from app.core.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: {"user_id": "t", "role": "admin"}
    try:
        with patch(
            "app.routers.router_metrics.prometheus.gpu_snapshot",
            new=AsyncMock(return_value=[{"hostname": "n1", "gpu": "0", "util_percent": 10.0}]),
        ):
            async with client as c:
                resp = await c.get("/api/metrics/gpu")
        assert resp.status_code == 200
        assert resp.json()["gpus"][0]["gpu"] == "0"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_metrics_gpu_503_when_prometheus_down(client):
    from app.main import app
    from app.core.deps import get_current_user
    from app.services.prometheus import PrometheusError

    app.dependency_overrides[get_current_user] = lambda: {"user_id": "t", "role": "admin"}
    try:
        with patch(
            "app.routers.router_metrics.prometheus.gpu_snapshot",
            new=AsyncMock(side_effect=PrometheusError("down")),
        ):
            async with client as c:
                resp = await c.get("/api/metrics/gpu")
        assert resp.status_code == 503
    finally:
        app.dependency_overrides.pop(get_current_user, None)


# ── TC-14-07: Agent tool executor 오류 내성 ─────────────────────────────────
# Iteration 16 개정: 구현체가 core → addon-agents/zip 으로 이동 (원 판정은 result.md 기록).

def _load_addon_module(key: str):
    import importlib.util
    from pathlib import Path

    path = Path("addon-agents/zip") / key / f"{key}-app.py"
    spec = importlib.util.spec_from_file_location(f"tc14_{key}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.asyncio
async def test_agent_tool_executors_return_error_dict():
    from app.services.prometheus import PrometheusError

    gpu_mod = _load_addon_module("gpu-monitor")
    hw_mod = _load_addon_module("hw-monitor")
    with (
        patch.object(gpu_mod.prometheus, "gpu_snapshot",
                     new=AsyncMock(side_effect=PrometheusError("down"))),
        patch.object(hw_mod.prometheus, "hardware_snapshot",
                     new=AsyncMock(side_effect=PrometheusError("down"))),
    ):
        g = await gpu_mod.TOOL_EXECUTORS["get_gpu_snapshot"]({})
        h = await hw_mod.TOOL_EXECUTORS["get_hardware_snapshot"]({})
    assert "error" in g and "error" in h


# ── TC-14-08: Orchestrator 배선 (Iteration 16 개정) ─────────────────────────

def test_orchestrator_wiring():
    from app.agents import orchestrator as orc

    assert orc._AGENT_MAP["gpu_monitoring"].addon_key == "gpu-monitor"
    assert orc._AGENT_MAP["hardware"].addon_key == "hw-monitor"
    assert "gpu_monitoring" in orc._VALID_INTENTS and "hardware" in orc._VALID_INTENTS
    assert "chat" not in orc._AGENT_MAP  # ExampleAgent 제거 확인

    with pytest.raises(ImportError):
        import app.agents.example_agent  # noqa: F401


def test_agent_tools_schema():
    gpu_mod = _load_addon_module("gpu-monitor")
    names = {t["name"] for t in gpu_mod._TOOLS}
    assert names == {"get_gpu_snapshot", "get_active_alerts", "query_promql"}
    assert set(gpu_mod.TOOL_EXECUTORS) == names  # tool ↔ executor 일치
