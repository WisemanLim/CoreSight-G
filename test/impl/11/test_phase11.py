"""Phase 12 — F25 Orchestrator 고도화 통합 시험 (Iteration 11).

TC-11-01~12: Registry 동적 라우팅, HITL 게이트, Reviewer 게이트, SSE 이벤트.
"""
import json
import os
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("ENV", "local")

from app.main import app  # noqa: E402
from app.agents.orchestrator import (  # noqa: E402
    _get_setting_bool,
    _registry_find_by_verb,
    _find_agent_by_type,
    _HIGH_RISK_INTENTS,
)


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client():
    from app.addon_agent_loader import init as addon_init
    from app.db import _PH, apply_column_migrations, execute_write, fetch_one, run_migrations, seed_default_admin
    from app.core.security import hash_password

    await run_migrations()
    await apply_column_migrations()
    await seed_default_admin()

    uid, pw = "p11_admin", "Admin11!"
    exists = await fetch_one(f"SELECT user_id FROM tbl_users WHERE user_id = {_PH}", (uid,))
    if not exists:
        await execute_write(
            f"INSERT INTO tbl_users (user_id, username, password, role) VALUES ({_PH},{_PH},{_PH},{_PH})",
            (uid, uid, hash_password(pw), "admin"),
        )
    await addon_init(app)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    await execute_write(f"DELETE FROM tbl_users WHERE user_id = {_PH}", (uid,))
    # 설정 복원
    for key in ("registry_dynamic_routing", "hitl_gate_enabled", "reviewer_gate_enabled"):
        await execute_write(f"DELETE FROM tbl_settings WHERE key = {_PH}", (key,))


@pytest_asyncio.fixture
async def token(client):
    resp = await client.post("/api/auth/login", json={"user_id": "p11_admin", "password": "Admin11!"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _parse_sse(content: bytes) -> list[dict]:
    """SSE 바이트 → {event, data} 리스트."""
    events = []
    current: dict = {}
    for line in content.decode("utf-8").splitlines():
        if line.startswith("event: "):
            current["event"] = line[7:]
        elif line.startswith("data: "):
            try:
                current["data"] = json.loads(line[6:])
            except Exception:
                current["data"] = line[6:]
        elif line == "" and current:
            events.append(current)
            current = {}
    return events


async def _stream_events(client, token, message: str) -> list[dict]:
    """SSE stream 전체 수신 → 이벤트 목록."""
    async with client.stream(
        "POST",
        "/api/agent/chat/stream",
        json={"message": message, "history": []},
        headers={"Authorization": f"Bearer {token}"},
    ) as resp:
        content = await resp.aread()
    return _parse_sse(content)


# ── TC-11-01: 기본값 — done 이벤트 정상 반환 ──────────────────────────────────

@pytest.mark.asyncio
async def test_default_stream_has_done_event(client, token):
    with patch("app.agents.orchestrator.call_ollama", new=AsyncMock(return_value="테스트 응답")):
        events = await _stream_events(client, token, "안녕")
    event_types = [e.get("event") for e in events]
    assert "done" in event_types


# ── TC-11-02: registry_dynamic_routing=true → registry_miss 이벤트 ───────────

@pytest.mark.asyncio
async def test_registry_dynamic_routing_emits_registry_miss(client, token):
    with (
        patch("app.agents.orchestrator._get_setting_bool", new=AsyncMock(side_effect=lambda k, d=False: k == "registry_dynamic_routing")),
        patch("app.agents.orchestrator.Orchestrator._classify_intent", new=AsyncMock(return_value=["unknown_intent"])),
        patch("app.agents.orchestrator.call_ollama", new=AsyncMock(return_value="응답")),
        patch("app.agents.orchestrator.Orchestrator._use_ollama", return_value=False),
        patch("app.agents.orchestrator.Orchestrator._claude_with_tools", new=AsyncMock(return_value="응답")),
    ):
        events = await _stream_events(client, token, "test message")
    event_types = [e.get("event") for e in events]
    assert "registry_miss" in event_types
    miss = next(e for e in events if e.get("event") == "registry_miss")
    assert miss["data"]["intent"] == "unknown_intent"
    assert "fallback" in miss["data"]


# ── TC-11-03: registry_dynamic_routing=false → registry_miss 없음 ─────────────

@pytest.mark.asyncio
async def test_no_registry_miss_when_disabled(client, token):
    with (
        patch("app.agents.orchestrator._get_setting_bool", new=AsyncMock(return_value=False)),
        patch("app.agents.orchestrator.call_ollama", new=AsyncMock(return_value="응답")),
    ):
        events = await _stream_events(client, token, "test message")
    event_types = [e.get("event") for e in events]
    assert "registry_miss" not in event_types


# ── TC-11-04: hitl_gate_enabled=true + delete intent + HITL addon → hitl_pending

@pytest.mark.asyncio
async def test_hitl_gate_blocks_high_risk_intent(client, token):
    fake_hitl = {"agent_key": "test_hitl", "agent_name": "Test HITL", "api_prefix": "/api/addon/test_hitl"}

    def setting_side_effect(key, default=False):
        return key == "hitl_gate_enabled"

    with (
        patch("app.agents.orchestrator._get_setting_bool", new=AsyncMock(side_effect=setting_side_effect)),
        patch("app.agents.orchestrator.Orchestrator._use_ollama", return_value=False),
        patch("app.agents.orchestrator.Orchestrator._classify_intent", new=AsyncMock(return_value=["delete"])),
        patch("app.agents.orchestrator._find_agent_by_type", new=AsyncMock(return_value=fake_hitl)),
        patch("app.agents.orchestrator.Orchestrator._claude_with_tools", new=AsyncMock(return_value="응답")),
    ):
        events = await _stream_events(client, token, "파일 삭제")
    event_types = [e.get("event") for e in events]
    assert "hitl_pending" in event_types
    pending = next(e for e in events if e.get("event") == "hitl_pending")
    assert pending["data"]["intent"] == "delete"
    assert "approval_id" in pending["data"]


# ── TC-11-05: hitl_gate_enabled=true + HITL addon 없음 → 정상 실행 ──────────────

@pytest.mark.asyncio
async def test_hitl_gate_passes_when_no_hitl_agent(client, token):
    def setting_side_effect(key, default=False):
        return key == "hitl_gate_enabled"

    with (
        patch("app.agents.orchestrator._get_setting_bool", new=AsyncMock(side_effect=setting_side_effect)),
        patch("app.agents.orchestrator.Orchestrator._use_ollama", return_value=False),
        patch("app.agents.orchestrator.Orchestrator._classify_intent", new=AsyncMock(return_value=["delete"])),
        patch("app.agents.orchestrator._find_agent_by_type", new=AsyncMock(return_value=None)),
        patch("app.agents.orchestrator.Orchestrator._claude_with_tools", new=AsyncMock(return_value="응답")),
    ):
        events = await _stream_events(client, token, "파일 삭제")
    event_types = [e.get("event") for e in events]
    assert "hitl_pending" not in event_types
    assert "done" in event_types


# ── TC-11-06: hitl_gate_enabled=false → 정상 실행 ────────────────────────────

@pytest.mark.asyncio
async def test_hitl_gate_disabled_passes(client, token):
    with (
        patch("app.agents.orchestrator._get_setting_bool", new=AsyncMock(return_value=False)),
        patch("app.agents.orchestrator.call_ollama", new=AsyncMock(return_value="응답")),
    ):
        events = await _stream_events(client, token, "삭제")
    event_types = [e.get("event") for e in events]
    assert "hitl_pending" not in event_types
    assert "done" in event_types


# ── TC-11-07: reviewer_gate_enabled=true + reviewer addon 없음 → review_gate 없음

@pytest.mark.asyncio
async def test_reviewer_gate_skipped_when_no_reviewer(client, token):
    def setting_side_effect(key, default=False):
        return key == "reviewer_gate_enabled"

    with (
        patch("app.agents.orchestrator._get_setting_bool", new=AsyncMock(side_effect=setting_side_effect)),
        patch("app.agents.orchestrator.Orchestrator._use_ollama", return_value=False),
        patch("app.agents.orchestrator.Orchestrator._classify_intent", new=AsyncMock(return_value=["general"])),
        patch("app.agents.orchestrator._find_agent_by_type", new=AsyncMock(return_value=None)),
        patch("app.agents.orchestrator.Orchestrator._claude_with_tools", new=AsyncMock(return_value="응답")),
    ):
        events = await _stream_events(client, token, "안녕")
    event_types = [e.get("event") for e in events]
    assert "review_gate" not in event_types
    assert "done" in event_types


# ── TC-11-08: _get_setting_bool 파싱 정확성 ──────────────────────────────────

@pytest.mark.asyncio
async def test_get_setting_bool_parsing():
    from app.db import _PH, execute_write
    test_key = "p11_test_bool"

    for val, expected in [("true", True), ("1", True), ("yes", True), ("false", False), ("0", False), ("no", False)]:
        await execute_write(
            f"INSERT OR REPLACE INTO tbl_settings (key, value) VALUES ({_PH},{_PH})",
            (test_key, val),
        )
        result = await _get_setting_bool(test_key)
        assert result == expected, f"val={val!r} expected={expected} got={result}"

    await execute_write(f"DELETE FROM tbl_settings WHERE key = {_PH}", (test_key,))


# ── TC-11-09: _registry_find_by_verb — DB 조회 정상 ──────────────────────────

@pytest.mark.asyncio
async def test_registry_find_by_verb():
    result = await _registry_find_by_verb("process")
    assert isinstance(result, list)


# ── TC-11-10: _find_agent_by_type — agent_type 필터 ─────────────────────────

@pytest.mark.asyncio
async def test_find_agent_by_type():
    result = await _find_agent_by_type("service")
    # None 또는 dict — 타입만 확인
    assert result is None or isinstance(result, dict)


# ── TC-11-11: run() — 기본 동작 (Ollama fallback) ────────────────────────────

@pytest.mark.asyncio
async def test_orchestrator_run_basic():
    from app.agents.orchestrator import Orchestrator

    orch = Orchestrator()
    with patch("app.agents.orchestrator.call_ollama", new=AsyncMock(return_value="테스트 응답")):
        result = await orch.run("안녕", [], model="ollama")
    assert isinstance(result, str)
    assert len(result) > 0


# ── TC-11-12: SSE stream Content-Type 헤더 확인 ──────────────────────────────

@pytest.mark.asyncio
async def test_stream_content_type_header(client, token):
    with patch("app.agents.orchestrator.call_ollama", new=AsyncMock(return_value="응답")):
        async with client.stream(
            "POST",
            "/api/agent/chat/stream",
            json={"message": "ping", "history": []},
            headers={"Authorization": f"Bearer {token}"},
        ) as resp:
            assert "text/event-stream" in resp.headers.get("content-type", "")


# ── F25 상수 확인 ──────────────────────────────────────────────────────────────

def test_high_risk_intents_defined():
    assert "delete" in _HIGH_RISK_INTENTS
    assert "execute" in _HIGH_RISK_INTENTS
    assert "deploy" in _HIGH_RISK_INTENTS
    assert "approve" in _HIGH_RISK_INTENTS
