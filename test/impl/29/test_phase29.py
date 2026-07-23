"""Phase 29 — P2-6 net-monitor addon 시험."""
import importlib.util
import os
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")

ADDON = Path("addon-agents/zip/net-monitor/net-monitor-app.py")


def _load():
    spec = importlib.util.spec_from_file_location("tc29_net-monitor", ADDON)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample(value: float, **labels) -> dict:
    return {"metric": labels, "value": [0, str(value)]}


# ── TC-29-01: 모듈 규약 ─────────────────────────────────────────────────────

def test_module_contract():
    module = _load()
    assert getattr(module, "router", None) is not None
    assert {t["name"] for t in module._TOOLS} == set(module.TOOL_EXECUTORS) == {
        "get_nic_snapshot", "get_active_alerts", "query_promql",
    }
    assert module.SYSTEM_PROMPT


# ── TC-29-02: 스냅샷 병합 ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_nic_snapshot_merges_and_sorts():
    module = _load()
    h = {"Hostname": "n1"}

    async def fake_query(promql: str):
        table = {
            "hw_nic_errors_total": [_sample(3.0, nic="eth1", **h), _sample(0.0, nic="eth0", **h)],
            "hw_nic_drops_total": [_sample(1.0, nic="eth1", **h)],
            "hw_nic_link_up": [_sample(0.0, nic="eth1", **h), _sample(1.0, nic="eth0", **h)],
            "hw_nic_rx_bytes_per_sec": [_sample(1e8, nic="eth0", **h)],
            "hw_nic_tx_bytes_per_sec": [_sample(5e7, nic="eth0", **h)],
        }
        return table.get(promql, [])

    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=fake_query)):
        result = await module.TOOL_EXECUTORS["get_nic_snapshot"]({})

    ifaces = result["interfaces"]
    assert [n["nic"] for n in ifaces] == ["eth0", "eth1"]  # 정렬
    eth1 = ifaces[1]
    assert eth1["errors_total"] == 3.0 and eth1["link_up"] == 0.0


# ── TC-29-03: Prometheus 다운 내성 ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_error_dict_when_prometheus_down():
    from app.services.prometheus import PrometheusError

    module = _load()
    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=PrometheusError("down"))):
        result = await module.TOOL_EXECUTORS["get_nic_snapshot"]({})
    assert "error" in result


# ── TC-29-04/05: 배선·패키지·시드 ───────────────────────────────────────────

def test_orchestrator_network_wiring():
    from app.agents import orchestrator as orc

    assert "network" in orc._VALID_INTENTS
    assert orc._AGENT_MAP["network"].addon_key == "net-monitor"


def test_zip_and_seed():
    with zipfile.ZipFile("addon-agents/zip/net-monitor.zip") as zf:
        assert set(zf.namelist()) == {
            "net-monitor-app.py", "net-monitor-meta.json", "net-monitor-worker-guide.md",
        }
    for path in ("sql/sqlite/02_seed.sql", "sql/pg/02_seed.sql"):
        src = open(path, encoding="utf-8").read()
        assert "'/api/addon/net-monitor', 1, 0, 'monitoring', 0, 1, 'system'" in src, path
        assert not any(
            "INSERT" in line and "'network'" in line and "tbl_agent_config" in line
            for line in src.splitlines()
        ), path
