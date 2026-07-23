"""Phase 20 — 트레이스(OTel/Jaeger) + trace-monitor addon 시험."""
import importlib.util
import os
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")


# ── TC-20-01/02: tracing 가드·내성 ──────────────────────────────────────────

def test_setup_tracing_noop_when_disabled():
    from fastapi import FastAPI
    from app.core.config import settings
    from app.core.tracing import setup_tracing

    with patch.object(settings, "otel_enabled", False):
        assert setup_tracing(FastAPI()) is False


def test_setup_tracing_swallows_init_failure():
    from fastapi import FastAPI
    from app.core.config import settings
    from app.core.tracing import setup_tracing

    with (
        patch.object(settings, "otel_enabled", True),
        patch(
            "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter",
            side_effect=RuntimeError("boom"),
        ),
    ):
        assert setup_tracing(FastAPI()) is False  # 예외 전파 없음


# ── TC-20-03: search_traces 요약 ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_traces_summarizes():
    from app.services import jaeger as svc

    raw = {
        "data": [
            {
                "traceID": "t1",
                "spans": [
                    {"operationName": "GET /x", "startTime": 100, "duration": 5000,
                     "tags": [{"key": "error", "value": True}]},
                    {"operationName": "child", "startTime": 200, "duration": 2000, "tags": []},
                ],
            },
            {
                "traceID": "t2",
                "spans": [
                    {"operationName": "GET /y", "startTime": 900, "duration": 1000, "tags": []},
                ],
            },
        ]
    }
    with patch.object(svc, "_get", new=AsyncMock(return_value=raw)):
        traces = await svc.search_traces("coresight-g-api")

    assert [t["trace_id"] for t in traces] == ["t2", "t1"]  # 최신순
    t1 = traces[1]
    assert t1["span_count"] == 2 and t1["duration_ms"] == 5.0 and t1["errors"] == 1
    assert t1["root_operation"] == "GET /x"


# ── TC-20-04: 연결 실패 ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_jaeger_error_on_connection_failure():
    import httpx
    from app.services import jaeger as svc

    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=httpx.ConnectError("boom"))):
        with pytest.raises(svc.JaegerError):
            await svc.services()


# ── TC-20-05/06/07: addon 규약·배선·패키지 ──────────────────────────────────

def test_trace_monitor_module_contract():
    path = Path("addon-agents/zip/trace-monitor/trace-monitor-app.py")
    spec = importlib.util.spec_from_file_location("testload_trace-monitor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert getattr(module, "router", None) is not None
    assert {t["name"] for t in module._TOOLS} == set(module.TOOL_EXECUTORS) == {
        "list_services", "search_traces",
    }
    assert module.SYSTEM_PROMPT


def test_orchestrator_trace_analysis_wiring():
    from app.agents import orchestrator as orc

    assert "trace_analysis" in orc._VALID_INTENTS
    assert orc._AGENT_MAP["trace_analysis"].addon_key == "trace-monitor"


def test_zip_package_contents():
    with zipfile.ZipFile("addon-agents/zip/trace-monitor.zip") as zf:
        names = set(zf.namelist())
    assert names == {"trace-monitor-app.py", "trace-monitor-meta.json", "trace-monitor-worker-guide.md"}
