"""Phase 26 — P2-3 gpu-profiler addon 시험."""
import importlib.util
import os
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")

ADDON = Path("addon-agents/zip/gpu-profiler/gpu-profiler-app.py")


def _load():
    spec = importlib.util.spec_from_file_location("tc26_gpu-profiler", ADDON)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample(value: float, **labels) -> dict:
    return {"metric": labels, "value": [0, str(value)]}


# ── TC-26-01: 모듈 규약 ─────────────────────────────────────────────────────

def test_module_contract():
    module = _load()
    assert getattr(module, "router", None) is not None
    assert {t["name"] for t in module._TOOLS} == set(module.TOOL_EXECUTORS) == {
        "get_gpu_profile", "get_throttled_gpus", "query_promql",
    }
    assert module.SYSTEM_PROMPT


# ── TC-26-02: 프로파일 병합 ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_gpu_profile_merges_and_sorts():
    module = _load()
    h = {"Hostname": "n1"}

    async def fake_query(promql: str):
        table = {
            "DCGM_FI_PROF_SM_OCCUPANCY": [_sample(0.7, gpu="1", **h), _sample(0.5, gpu="0", **h)],
            "DCGM_FI_PROF_PIPE_TENSOR_ACTIVE": [_sample(0.3, gpu="0", **h)],
            "DCGM_FI_DEV_CLOCK_THROTTLE_REASONS": [_sample(1.0, gpu="0", **h)],
        }
        return table.get(promql, [])

    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=fake_query)):
        gpus = await module.TOOL_EXECUTORS["get_gpu_profile"]({})

    assert [g["gpu"] for g in gpus["gpus"]] == ["0", "1"]  # 정렬
    assert gpus["gpus"][0]["throttle_reasons"] == 1.0


# ── TC-26-03: throttle 필터 ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_throttled_gpus_filters():
    module = _load()
    h = {"Hostname": "n1"}

    async def fake_query(promql: str):
        if promql == "DCGM_FI_DEV_CLOCK_THROTTLE_REASONS":
            return [_sample(1.0, gpu="3", **h), _sample(0.0, gpu="0", **h)]
        return []

    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=fake_query)):
        result = await module.TOOL_EXECUTORS["get_throttled_gpus"]({})

    assert result["count"] == 1 and result["gpus"][0]["gpu"] == "3"


# ── TC-26-04: Prometheus 다운 내성 ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_error_dict_when_prometheus_down():
    from app.services.prometheus import PrometheusError

    module = _load()
    with patch.object(module.prometheus, "query", new=AsyncMock(side_effect=PrometheusError("down"))):
        p = await module.TOOL_EXECUTORS["get_gpu_profile"]({})
        t = await module.TOOL_EXECUTORS["get_throttled_gpus"]({})
    assert "error" in p and "error" in t


# ── TC-26-05/06: 배선·패키지·시드 ───────────────────────────────────────────

def test_orchestrator_gpu_profiling_wiring():
    from app.agents import orchestrator as orc

    assert "gpu_profiling" in orc._VALID_INTENTS
    assert orc._AGENT_MAP["gpu_profiling"].addon_key == "gpu-profiler"


def test_zip_and_seed():
    with zipfile.ZipFile("addon-agents/zip/gpu-profiler.zip") as zf:
        assert set(zf.namelist()) == {
            "gpu-profiler-app.py", "gpu-profiler-meta.json", "gpu-profiler-worker-guide.md",
        }
    for path in ("sql/sqlite/02_seed.sql", "sql/pg/02_seed.sql"):
        src = open(path, encoding="utf-8").read()
        assert "'/api/addon/gpu-profiler', 1, 0, 'monitoring', 0, 1, 'system'" in src, path
        assert not any(
            "INSERT" in line and "'gpu_profiling'" in line and "tbl_agent_config" in line
            for line in src.splitlines()
        ), path
