"""Phase 24 — P2-1 storage-monitor addon 시험."""
import importlib.util
import os
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")

ADDON = Path("addon-agents/zip/storage-monitor/storage-monitor-app.py")


def _load():
    spec = importlib.util.spec_from_file_location("tc24_storage-monitor", ADDON)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample(value: float, **labels) -> dict:
    return {"metric": labels, "value": [0, str(value)]}


# ── TC-24-01: 모듈 규약 ─────────────────────────────────────────────────────

def test_module_contract():
    module = _load()
    assert getattr(module, "router", None) is not None
    assert {t["name"] for t in module._TOOLS} == set(module.TOOL_EXECUTORS) == {
        "get_storage_snapshot", "get_active_alerts", "query_promql",
    }
    assert module.SYSTEM_PROMPT


# ── TC-24-02: 스냅샷 병합 ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_storage_snapshot_merges_devices():
    module = _load()

    async def fake_query(promql: str):
        h = {"Hostname": "n1"}
        table = {
            "hw_disk_read_latency_ms": [_sample(5.0, device="sda", **h)],
            "hw_disk_write_latency_ms": [_sample(7.0, device="sda", **h)],
            "hw_smart_healthy": [_sample(0.0, device="sda", **h)],
            "hw_nvme_wear_level_percent": [],
            "hw_disk_iops": [
                _sample(100.0, device="sda", op="read", **h),
                _sample(50.0, device="sda", op="write", **h),
            ],
            "hw_raid_degraded": [_sample(1.0, controller="c0", **h)],
        }
        return table.get(promql, [])

    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=fake_query)):
        snap = await module.TOOL_EXECUTORS["get_storage_snapshot"]({})

    dev = snap["devices"][0]
    assert dev["device"] == "sda" and dev["read_latency_ms"] == 5.0
    assert dev["iops_read"] == 100.0 and dev["iops_write"] == 50.0
    assert dev["smart_healthy"] == 0.0
    assert snap["raid"][0]["degraded"] is True


# ── TC-24-03: Prometheus 다운 내성 ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_snapshot_error_dict_when_prometheus_down():
    from app.services.prometheus import PrometheusError

    module = _load()
    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=PrometheusError("down"))):
        result = await module.TOOL_EXECUTORS["get_storage_snapshot"]({})
    assert "error" in result


# ── TC-24-04/05/06: 배선·패키지·시드 ────────────────────────────────────────

def test_orchestrator_storage_wiring():
    from app.agents import orchestrator as orc

    assert "storage" in orc._VALID_INTENTS
    assert orc._AGENT_MAP["storage"].addon_key == "storage-monitor"


def test_zip_package_contents():
    with zipfile.ZipFile("addon-agents/zip/storage-monitor.zip") as zf:
        names = set(zf.namelist())
    assert names == {"storage-monitor-app.py", "storage-monitor-meta.json", "storage-monitor-worker-guide.md"}


def test_seed_registers_as_addon():
    for path in ("sql/sqlite/02_seed.sql", "sql/pg/02_seed.sql"):
        src = open(path, encoding="utf-8").read()
        assert "'/api/addon/storage-monitor', 1, 0, 'monitoring', 0, 1, 'system'" in src, path
        assert not any(
            "INSERT" in line and "'storage'" in line and "tbl_agent_config" in line
            for line in src.splitlines()
        ), path
