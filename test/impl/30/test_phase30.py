"""Phase 30 — P2-7 workload-correlator addon 시험 (P2 로드맵 완결)."""
import importlib.util
import os
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")

ADDON = Path("addon-agents/zip/workload-correlator/workload-correlator-app.py")


def _load():
    spec = importlib.util.spec_from_file_location("tc30_workload-correlator", ADDON)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample(value: float, **labels) -> dict:
    return {"metric": labels, "value": [0, str(value)]}


_ROWS = [
    _sample(18000.0, Hostname="n1", gpu="0", pid="1", job_id="j1", user="alice"),
    _sample(12000.0, Hostname="n1", gpu="1", pid="2", job_id="j1", user="alice"),
    _sample(27000.0, Hostname="n1", gpu="2", pid="3", job_id="j2", user="bob"),
]


# ── TC-30-01: 모듈 규약 ─────────────────────────────────────────────────────

def test_module_contract():
    module = _load()
    assert getattr(module, "router", None) is not None
    assert {t["name"] for t in module._TOOLS} == set(module.TOOL_EXECUTORS) == {
        "get_gpu_process_map", "get_usage_by_job", "get_usage_by_user",
    }
    assert module.SYSTEM_PROMPT


# ── TC-30-02: 프로세스 맵 ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_process_map_sorted():
    module = _load()
    with patch.object(module.prometheus, "query", new=AsyncMock(return_value=_ROWS)):
        result = await module.TOOL_EXECUTORS["get_gpu_process_map"]({})
    assert [p["gpu"] for p in result["processes"]] == ["0", "1", "2"]


# ── TC-30-03: job 집계 ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_usage_by_job_aggregates_distributed_job():
    module = _load()
    with patch.object(module.prometheus, "query", new=AsyncMock(return_value=_ROWS)):
        result = await module.TOOL_EXECUTORS["get_usage_by_job"]({})

    jobs = {j["job_id"]: j for j in result["jobs"]}
    assert jobs["j1"]["total_memory_mib"] == 30000.0
    assert jobs["j1"]["gpus"] == ["0", "1"]
    assert jobs["j1"]["process_count"] == 2
    assert result["jobs"][0]["job_id"] == "j1"  # 30000 > 27000, 내림차순


# ── TC-30-04: user 집계 ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_usage_by_user_aggregates():
    module = _load()
    with patch.object(module.prometheus, "query", new=AsyncMock(return_value=_ROWS)):
        result = await module.TOOL_EXECUTORS["get_usage_by_user"]({})

    users = {u["user"]: u for u in result["users"]}
    assert users["alice"]["total_memory_mib"] == 30000.0
    assert users["bob"]["total_memory_mib"] == 27000.0


# ── TC-30-05: Prometheus 다운 내성 ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_error_dicts_when_prometheus_down():
    from app.services.prometheus import PrometheusError

    module = _load()
    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=PrometheusError("down"))):
        p = await module.TOOL_EXECUTORS["get_gpu_process_map"]({})
        j = await module.TOOL_EXECUTORS["get_usage_by_job"]({})
        u = await module.TOOL_EXECUTORS["get_usage_by_user"]({})
    assert "error" in p and "error" in j and "error" in u


# ── TC-30-06/07: 배선·패키지·시드 ───────────────────────────────────────────

def test_orchestrator_workload_correlation_wiring():
    from app.agents import orchestrator as orc

    assert "workload_correlation" in orc._VALID_INTENTS
    assert orc._AGENT_MAP["workload_correlation"].addon_key == "workload-correlator"


def test_zip_and_seed():
    with zipfile.ZipFile("addon-agents/zip/workload-correlator.zip") as zf:
        assert set(zf.namelist()) == {
            "workload-correlator-app.py", "workload-correlator-meta.json",
            "workload-correlator-worker-guide.md",
        }
    for path in ("sql/sqlite/02_seed.sql", "sql/pg/02_seed.sql"):
        src = open(path, encoding="utf-8").read()
        assert "'/api/addon/workload-correlator', 1, 0, 'monitoring', 0, 1, 'system'" in src, path
        assert not any(
            "INSERT" in line and "'workload_correlation'" in line and "tbl_agent_config" in line
            for line in src.splitlines()
        ), path


# ── P2 로드맵 완결 확인 ──────────────────────────────────────────────────────

def test_all_p2_addons_registered():
    """PRD P2-1~7 전체가 ADDON 에이전트(is_builtin=0)로 등록됐는지 확인."""
    expected = {
        "log-analyzer", "trace-monitor", "storage-monitor", "bmc-monitor",
        "gpu-profiler", "capacity-planner", "anomaly-detector", "net-monitor",
        "workload-correlator",
    }
    for path in ("sql/sqlite/02_seed.sql", "sql/pg/02_seed.sql"):
        src = open(path, encoding="utf-8").read()
        for key in expected:
            assert f"'/api/addon/{key}', 1, 0, 'monitoring', 0, 1, 'system'" in src, (path, key)
