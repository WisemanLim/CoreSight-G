"""Phase 25 — P2-2 bmc-monitor addon 시험."""
import importlib.util
import os
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")

ADDON = Path("addon-agents/zip/bmc-monitor/bmc-monitor-app.py")


def _load():
    spec = importlib.util.spec_from_file_location("tc25_bmc-monitor", ADDON)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample(value: float, **labels) -> dict:
    return {"metric": labels, "value": [0, str(value)]}


# ── TC-25-01: 모듈 규약 ─────────────────────────────────────────────────────

def test_module_contract():
    module = _load()
    assert getattr(module, "router", None) is not None
    assert {t["name"] for t in module._TOOLS} == set(module.TOOL_EXECUTORS) == {
        "get_bmc_sensors", "get_bmc_events", "get_active_alerts",
    }
    assert module.SYSTEM_PROMPT


# ── TC-25-02: 센서 병합 ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_bmc_sensors_merge():
    module = _load()
    h = {"Hostname": "n1"}

    async def fake_query(promql: str):
        table = {
            "hw_fan_speed_rpm": [_sample(5000.0, fan="fan1", **h), _sample(800.0, fan="fan2", **h)],
            "hw_voltage_volts": [_sample(12.1, rail="12V", **h)],
            "hw_psu_status": [_sample(1.0, psu="psu1", **h)],
            "hw_inlet_temp_celsius": [_sample(23.0, **h)],
            "hw_bmc_power_watts": [_sample(1500.0, **h)],
        }
        return table.get(promql, [])

    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=fake_query)):
        snap = await module.TOOL_EXECUTORS["get_bmc_sensors"]({})

    node = snap["nodes"][0]
    assert node["fans"] == {"fan1": 5000.0, "fan2": 800.0}
    assert node["voltages"]["12V"] == 12.1 and node["psu"]["psu1"] == 1.0
    assert node["inlet_temp_celsius"] == 23.0 and node["chassis_power_watts"] == 1500.0


# ── TC-25-03: 이벤트 조회 ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_bmc_events_query():
    module = _load()
    entries = [{"ts": 1, "line": "iDRAC: RAID DEGRADED", "labels": {"job": "bmc"}}]
    with patch.object(module.loki, "search", new=AsyncMock(return_value=entries)):
        result = await module.TOOL_EXECUTORS["get_bmc_events"]({"level": "error"})
    assert result["query"] == '{job="bmc", level="error"}'
    assert result["count"] == 1


# ── TC-25-04: 소스 다운 내성 ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_error_dicts_when_sources_down():
    from app.services.loki import LokiError
    from app.services.prometheus import PrometheusError

    module = _load()
    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=PrometheusError("down"))):
        s = await module.TOOL_EXECUTORS["get_bmc_sensors"]({})
    with patch.object(module.loki, "search", new=AsyncMock(side_effect=LokiError("down"))):
        e = await module.TOOL_EXECUTORS["get_bmc_events"]({})
    assert "error" in s and "error" in e


# ── TC-25-05/06: 배선·패키지·시드 ───────────────────────────────────────────

def test_orchestrator_bmc_wiring():
    from app.agents import orchestrator as orc

    assert "bmc" in orc._VALID_INTENTS
    assert orc._AGENT_MAP["bmc"].addon_key == "bmc-monitor"


def test_zip_and_seed():
    with zipfile.ZipFile("addon-agents/zip/bmc-monitor.zip") as zf:
        assert set(zf.namelist()) == {
            "bmc-monitor-app.py", "bmc-monitor-meta.json", "bmc-monitor-worker-guide.md",
        }
    for path in ("sql/sqlite/02_seed.sql", "sql/pg/02_seed.sql"):
        src = open(path, encoding="utf-8").read()
        assert "'/api/addon/bmc-monitor', 1, 0, 'monitoring', 0, 1, 'system'" in src, path
        assert not any(
            "INSERT" in line and "'bmc'" in line and "tbl_agent_config" in line
            for line in src.splitlines()
        ), path
