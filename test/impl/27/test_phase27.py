"""Phase 27 — P2-4 capacity-planner addon 시험."""
import importlib.util
import os
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")

ADDON = Path("addon-agents/zip/capacity-planner/capacity-planner-app.py")


def _load():
    spec = importlib.util.spec_from_file_location("tc27_capacity-planner", ADDON)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample(value: float, **labels) -> dict:
    return {"metric": labels, "value": [0, str(value)]}


# ── TC-27-01: 모듈 규약 ─────────────────────────────────────────────────────

def test_module_contract():
    module = _load()
    assert getattr(module, "router", None) is not None
    assert {t["name"] for t in module._TOOLS} == set(module.TOOL_EXECUTORS) == {
        "get_underutilized_gpus", "get_efficiency_report", "get_cardinality_summary",
    }
    assert module.SYSTEM_PROMPT


# ── TC-27-02: 저활용 필터 ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_underutilized_filters_by_threshold():
    module = _load()
    h = {"Hostname": "n1"}

    async def fake_query(promql: str):
        assert promql == "avg_over_time(DCGM_FI_DEV_GPU_UTIL[24h])"
        return [_sample(9.0, gpu="3", **h), _sample(80.0, gpu="0", **h)]

    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=fake_query)):
        result = await module.TOOL_EXECUTORS["get_underutilized_gpus"]({})

    assert result["count"] == 1 and result["gpus"][0]["gpu"] == "3"


# ── TC-27-03: 효율 리포트 병합 ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_efficiency_report_merges():
    module = _load()
    h = {"Hostname": "n1", "gpu": "0"}

    async def fake_query(promql: str):
        if promql == "avg_over_time(DCGM_FI_DEV_GPU_UTIL[24h])":
            return [_sample(60.0, **h)]
        if promql == "avg_over_time(DCGM_FI_DEV_FB_USED[24h])":
            return [_sample(40960.0, **h)]
        if promql == "DCGM_FI_DEV_FB_TOTAL":
            return [_sample(81920.0, **h)]
        return []

    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=fake_query)):
        report = await module.TOOL_EXECUTORS["get_efficiency_report"]({})

    assert report["fleet_avg_util_percent"] == 60.0
    assert report["gpus"][0]["avg_vram_percent"] == 50.0


# ── TC-27-04: 카디널리티 요약 ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cardinality_summary_sorted():
    module = _load()

    async def fake_query(promql: str):
        return [
            _sample(5.0, __name__="hw_fan_speed_rpm"),
            _sample(28.0, __name__="DCGM_FI_DEV_GPU_UTIL"),
        ]

    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=fake_query)):
        result = await module.TOOL_EXECUTORS["get_cardinality_summary"]({})

    assert result["total_series"] == 33
    assert result["by_metric"][0]["metric"] == "DCGM_FI_DEV_GPU_UTIL"  # 내림차순


# ── TC-27-05: Prometheus 다운 내성 ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_error_dicts_when_prometheus_down():
    from app.services.prometheus import PrometheusError

    module = _load()
    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=PrometheusError("down"))):
        u = await module.TOOL_EXECUTORS["get_underutilized_gpus"]({})
        e = await module.TOOL_EXECUTORS["get_efficiency_report"]({})
        c = await module.TOOL_EXECUTORS["get_cardinality_summary"]({})
    assert "error" in u and "error" in e and "error" in c


# ── TC-27-06/07: 배선·패키지·시드 ───────────────────────────────────────────

def test_orchestrator_capacity_planning_wiring():
    from app.agents import orchestrator as orc

    assert "capacity_planning" in orc._VALID_INTENTS
    assert orc._AGENT_MAP["capacity_planning"].addon_key == "capacity-planner"


def test_zip_and_seed():
    with zipfile.ZipFile("addon-agents/zip/capacity-planner.zip") as zf:
        assert set(zf.namelist()) == {
            "capacity-planner-app.py", "capacity-planner-meta.json", "capacity-planner-worker-guide.md",
        }
    for path in ("sql/sqlite/02_seed.sql", "sql/pg/02_seed.sql"):
        src = open(path, encoding="utf-8").read()
        assert "'/api/addon/capacity-planner', 1, 0, 'monitoring', 0, 1, 'system'" in src, path
        assert not any(
            "INSERT" in line and "'capacity_planning'" in line and "tbl_agent_config" in line
            for line in src.splitlines()
        ), path
