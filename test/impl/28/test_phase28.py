"""Phase 28 — P2-5 anomaly-detector addon 시험."""
import importlib.util
import os
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")

ADDON = Path("addon-agents/zip/anomaly-detector/anomaly-detector-app.py")


def _load():
    spec = importlib.util.spec_from_file_location("tc28_anomaly-detector", ADDON)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ── TC-28-01: 모듈 규약 ─────────────────────────────────────────────────────

def test_module_contract():
    module = _load()
    assert getattr(module, "router", None) is not None
    assert {t["name"] for t in module._TOOLS} == set(module.TOOL_EXECUTORS) == {
        "detect_metric_anomalies", "correlate_alerts",
    }
    assert module.SYSTEM_PROMPT


# ── TC-28-02: z-score 계산 ──────────────────────────────────────────────────

def test_zscores_flags_outlier():
    module = _load()
    values = [10.0, 11.0, 9.0, 10.0, 11.0, 9.0, 10.0, 11.0, 9.0, 10.0, 11.0, 9.0, 200.0]  # 마지막 값 = 명백한 이상치
    zs = module._zscores(values)
    assert abs(zs[-1]) > 3.0
    assert all(abs(z) < 1.5 for z in zs[:-1])


def test_zscores_zero_stdev_returns_zero():
    module = _load()
    assert module._zscores([5.0, 5.0, 5.0]) == [0.0, 0.0, 0.0]


@pytest.mark.asyncio
async def test_detect_metric_anomalies_end_to_end():
    module = _load()
    values = [[str(i), str(v)] for i, v in enumerate([10, 11, 9, 10, 11, 9, 10, 11, 9, 10, 11, 9, 200])]
    series = [{"metric": {"gpu": "0"}, "values": values}]

    with patch.object(module.prometheus, "query_range", new=AsyncMock(return_value=series)):
        result = await module.TOOL_EXECUTORS["detect_metric_anomalies"]({"promql": "X", "hours": 1})

    assert result["count"] == 1
    assert result["anomalies"][0]["value"] == 200.0


# ── TC-28-03: 표본 부족 스킵 ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_skips_short_series():
    module = _load()
    series = [{"metric": {"gpu": "0"}, "values": [["0", "10"], ["1", "999"]]}]  # 표본 2개 < 5

    with patch.object(module.prometheus, "query_range", new=AsyncMock(return_value=series)):
        result = await module.TOOL_EXECUTORS["detect_metric_anomalies"]({"promql": "X"})

    assert result["count"] == 0


# ── TC-28-04: 알람 상관 그룹핑 ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_correlate_alerts_groups_by_hostname():
    module = _load()
    alerts = [
        {"labels": {"alertname": "A", "Hostname": "n1", "severity": "critical"}, "state": "firing"},
        {"labels": {"alertname": "B", "Hostname": "n1", "severity": "warning"}, "state": "pending"},
        {"labels": {"alertname": "C", "Hostname": "n2", "severity": "critical"}, "state": "firing"},
    ]
    with patch.object(module.prometheus, "active_alerts", new=AsyncMock(return_value=alerts)):
        result = await module.TOOL_EXECUTORS["correlate_alerts"]({})

    assert result["total_active"] == 3
    assert result["correlated_targets"] == 1
    assert "n1" in result["groups"] and "n2" not in result["groups"]


# ── TC-28-05: Prometheus 다운 내성 ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_error_dicts_when_prometheus_down():
    from app.services.prometheus import PrometheusError

    module = _load()
    with patch.object(module.prometheus, "query_range", new=AsyncMock(side_effect=PrometheusError("down"))):
        d = await module.TOOL_EXECUTORS["detect_metric_anomalies"]({"promql": "X"})
    with patch.object(module.prometheus, "active_alerts", new=AsyncMock(side_effect=PrometheusError("down"))):
        c = await module.TOOL_EXECUTORS["correlate_alerts"]({})
    assert "error" in d and "error" in c


# ── TC-28-06/07: 배선·패키지·시드 ───────────────────────────────────────────

def test_orchestrator_anomaly_detection_wiring():
    from app.agents import orchestrator as orc

    assert "anomaly_detection" in orc._VALID_INTENTS
    assert orc._AGENT_MAP["anomaly_detection"].addon_key == "anomaly-detector"


def test_zip_and_seed():
    with zipfile.ZipFile("addon-agents/zip/anomaly-detector.zip") as zf:
        assert set(zf.namelist()) == {
            "anomaly-detector-app.py", "anomaly-detector-meta.json", "anomaly-detector-worker-guide.md",
        }
    for path in ("sql/sqlite/02_seed.sql", "sql/pg/02_seed.sql"):
        src = open(path, encoding="utf-8").read()
        assert "'/api/addon/anomaly-detector', 1, 0, 'monitoring', 0, 1, 'system'" in src, path
        assert not any(
            "INSERT" in line and "'anomaly_detection'" in line and "tbl_agent_config" in line
            for line in src.splitlines()
        ), path
