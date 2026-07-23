"""Phase 19 — 로그 수집·검색(Loki) + log-analyzer addon 시험."""
import importlib.util
import os
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")


# ── TC-19-01: build_logql ───────────────────────────────────────────────────

def test_build_logql_combinations():
    from app.services.loki import build_logql

    assert build_logql() == '{job=~".+"}'
    assert build_logql(job="dmesg") == '{job="dmesg"}'
    assert build_logql(job="bmc", level="error") == '{job="bmc", level="error"}'
    assert build_logql(keyword="Xid") == '{job=~".+"} |~ "(?i)Xid"'
    assert build_logql(keyword='a"b') == '{job=~".+"} |~ "(?i)a\\"b"'


# ── TC-19-02: search 평탄화·정렬 ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_flattens_and_sorts():
    from app.services import loki as svc

    raw = {
        "status": "success",
        "data": {
            "result": [
                {"stream": {"job": "dmesg"}, "values": [["100", "old"], ["300", "new"]]},
                {"stream": {"job": "bmc"}, "values": [["200", "mid"]]},
            ]
        },
    }
    with patch.object(svc, "_get", new=AsyncMock(return_value=raw)):
        entries = await svc.search('{job=~".+"}', minutes=10, limit=2)

    assert [e["line"] for e in entries] == ["new", "mid"]  # 내림차순 + limit 2
    assert entries[0]["labels"]["job"] == "dmesg"


# ── TC-19-03: 연결 실패 ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_loki_error_on_connection_failure():
    import httpx
    from app.services import loki as svc

    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=httpx.ConnectError("boom"))):
        with pytest.raises(svc.LokiError):
            await svc.labels()


# ── TC-19-04/05/06 (Iteration 22 개정 — Addon-first: core /api/logs 라우터 제거) ──

def _load_log_analyzer():
    path = Path("addon-agents/zip/log-analyzer/log-analyzer-app.py")
    spec = importlib.util.spec_from_file_location("tc19_log-analyzer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.asyncio
async def test_core_logs_router_removed():
    """로그 조회는 addon 전용 — core /api/logs/* 는 존재하지 않아야 한다."""
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        for path in ("/api/logs/search", "/api/logs/labels"):
            resp = await c.get(path)
            assert resp.status_code == 404, path


@pytest.mark.asyncio
async def test_addon_search_logs_ok():
    module = _load_log_analyzer()
    with patch.object(module.loki, "search",
                      new=AsyncMock(return_value=[{"ts": 1, "line": "x", "labels": {}}])):
        result = await module.TOOL_EXECUTORS["search_logs"]({"job": "dmesg"})
    assert result["query"] == '{job="dmesg"}' and result["count"] == 1


@pytest.mark.asyncio
async def test_addon_search_logs_error_dict_when_loki_down():
    from app.services.loki import LokiError

    module = _load_log_analyzer()
    with patch.object(module.loki, "search", new=AsyncMock(side_effect=LokiError("down"))):
        result = await module.TOOL_EXECUTORS["search_logs"]({})
    assert "error" in result  # 예외 미전파 — error dict


# ── TC-19-07/08/09: addon 규약·배선·패키지 ──────────────────────────────────

def test_log_analyzer_module_contract():
    path = Path("addon-agents/zip/log-analyzer/log-analyzer-app.py")
    spec = importlib.util.spec_from_file_location("testload_log-analyzer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert getattr(module, "router", None) is not None
    assert {t["name"] for t in module._TOOLS} == set(module.TOOL_EXECUTORS) == {
        "search_logs", "recent_errors",
    }
    assert module.SYSTEM_PROMPT


def test_orchestrator_log_analysis_wiring():
    from app.agents import orchestrator as orc

    assert "log_analysis" in orc._VALID_INTENTS
    assert orc._AGENT_MAP["log_analysis"].addon_key == "log-analyzer"


def test_zip_package_contents():
    with zipfile.ZipFile("addon-agents/zip/log-analyzer.zip") as zf:
        names = set(zf.namelist())
    assert names == {"log-analyzer-app.py", "log-analyzer-meta.json", "log-analyzer-worker-guide.md"}
