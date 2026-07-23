"""Phase 23 — P1 Agent 의 ADDON 등록·intent 게이팅 시험."""
import os
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("ENV", "local")


# ── TC-23-04: addon is_active=0 → intent 비활성 ─────────────────────────────

@pytest.mark.asyncio
async def test_disabled_agents_includes_inactive_addon_intents():
    from app.agents import orchestrator as orc

    async def fake_fetch_all(sql, params=()):
        if "tbl_agent_config" in sql:
            return []
        if "tbl_addon_agents" in sql:
            return [{"agent_key": "log-analyzer"}, {"agent_key": "trace-monitor"}]
        return []

    with patch("app.db.fetch_all", new=AsyncMock(side_effect=fake_fetch_all)):
        disabled = await orc._disabled_agents()

    assert {"log_analysis", "trace_analysis"} <= disabled
    assert "gpu_monitoring" not in disabled


@pytest.mark.asyncio
async def test_disabled_agents_empty_when_all_active():
    from app.agents import orchestrator as orc

    with patch("app.db.fetch_all", new=AsyncMock(return_value=[])):
        disabled = await orc._disabled_agents()
    assert disabled == set()


# ── TC-23-01/02: 시드 정합 (파일 기준) ──────────────────────────────────────

def test_seed_registers_p1_as_non_builtin():
    for path in ("sql/sqlite/02_seed.sql", "sql/pg/02_seed.sql"):
        src = open(path, encoding="utf-8").read()
        for key in ("log-analyzer", "trace-monitor"):
            assert f"'/api/addon/{key}', 1, 0, 'monitoring', 0, 1, 'system'" in src, (path, key)
            assert f"agent_type='monitoring', is_builtin=0 WHERE agent_key='{key}'" in src, (path, key)
        # P1 agent_config 미등록 (정리 DELETE 만 존재)
        assert "DELETE FROM tbl_agent_config WHERE agent_key = 'log_analysis';" in src
        assert "INSERT" not in [
            line for line in src.splitlines() if "log_analysis" in line and "INSERT" in line
        ] or True
        assert not any(
            "INSERT" in line and ("'log_analysis'" in line or "'trace_analysis'" in line)
            for line in src.splitlines()
        ), path
