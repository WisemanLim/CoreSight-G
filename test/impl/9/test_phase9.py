"""Phase 10 — F23 Agent Registry v2 통합 시험 (Iteration 9).

TC-9-01~12: Registry v2 컬럼, capability search, Agent Card, heartbeat, health.
"""
import io
import json
import os
import zipfile

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("ENV", "local")

from app.main import app  # noqa: E402


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client():
    from app.addon_agent_loader import init as addon_init
    from app.db import _PH, apply_column_migrations, execute_write, fetch_one, run_migrations, seed_default_admin
    from app.core.security import hash_password

    await run_migrations()
    await apply_column_migrations()
    await seed_default_admin()

    uid, pw = "p9_admin", "Admin9!"
    exists = await fetch_one(f"SELECT user_id FROM tbl_users WHERE user_id = {_PH}", (uid,))
    if not exists:
        await execute_write(
            f"INSERT INTO tbl_users (user_id, username, password, role) VALUES ({_PH},{_PH},{_PH},{_PH})",
            (uid, uid, hash_password(pw), "admin"),
        )
    await addon_init(app)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    # 정리
    await execute_write(f"DELETE FROM tbl_users WHERE user_id = {_PH}", (uid,))
    await execute_write("DELETE FROM tbl_agent_registry WHERE agent_key LIKE 'p9_%'")


@pytest_asyncio.fixture
async def token(client):
    resp = await client.post("/api/auth/login", json={"user_id": "p9_admin", "password": "Admin9!"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def registered_agent(client, token):
    """테스트용 외부 Agent 등록 후 key 반환."""
    caps = [
        {"verb": "retrieve", "domain": "knowledge.hr", "description": "HR 문서 검색"},
        {"verb": "search", "domain": "knowledge.policy", "description": "정책 검색"},
    ]
    resp = await client.post(
        "/api/agent-registry/",
        json={
            "agent_key": "p9_hr_agent",
            "agent_name": "HR Knowledge Agent",
            "protocol": "a2a",
            "agent_card_url": "http://localhost:9001/.well-known/agent-card.json",
            "agent_type": "rag",
            "capabilities_json": json.dumps(caps),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    yield "p9_hr_agent"
    await client.delete(
        "/api/agent-registry/p9_hr_agent",
        headers={"Authorization": f"Bearer {token}"},
    )


def _make_zip(name: str, files: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for fname, content in files.items():
            zf.writestr(fname, content)
    return buf.getvalue()


# ── TC-9-01: 목록 v2 필드 ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_registry_list_has_v2_fields(client, token, registered_agent):
    resp = await client.get("/api/agent-registry/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    agents = resp.json()["agents"]
    assert any(a["agent_key"] == "p9_hr_agent" for a in agents)
    hr = next(a for a in agents if a["agent_key"] == "p9_hr_agent")
    assert "agent_type" in hr
    assert "lifecycle_state" in hr
    assert "health_dot" in hr
    assert hr["agent_type"] == "rag"
    assert hr["lifecycle_state"] == "active"


# ── TC-9-02: 외부 Agent 등록 ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_with_capabilities(client, token):
    caps = [{"verb": "process", "domain": "service.billing", "description": "청구 처리"}]
    resp = await client.post(
        "/api/agent-registry/",
        json={
            "agent_key": "p9_billing_svc",
            "agent_name": "Billing Service",
            "agent_type": "service",
            "capabilities_json": json.dumps(caps),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["agent_key"] == "p9_billing_svc"
    # 정리
    await client.delete("/api/agent-registry/p9_billing_svc", headers={"Authorization": f"Bearer {token}"})


# ── TC-9-03: capability search — verb 필터 ────────────────────────────────────

@pytest.mark.asyncio
async def test_search_by_verb(client, token, registered_agent):
    resp = await client.post(
        "/api/agent-registry/search",
        json={"capabilities": ["retrieve"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    keys = [a["agent_key"] for a in data["agents"]]
    assert "p9_hr_agent" in keys


# ── TC-9-04: capability search — domain_prefix 필터 ──────────────────────────

@pytest.mark.asyncio
async def test_search_by_domain_prefix(client, token, registered_agent):
    resp = await client.post(
        "/api/agent-registry/search",
        json={"domain_prefix": "knowledge."},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    keys = [a["agent_key"] for a in resp.json()["agents"]]
    assert "p9_hr_agent" in keys


# ── TC-9-05: capability search — agent_type 필터 ──────────────────────────────

@pytest.mark.asyncio
async def test_search_by_agent_type(client, token, registered_agent):
    resp = await client.post(
        "/api/agent-registry/search",
        json={"agent_type": "rag"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    for agent in resp.json()["agents"]:
        assert agent["agent_type"] == "rag"


# ── TC-9-06: Agent Card 자동 생성 ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_agent_card_auto_generated(client, token, registered_agent):
    resp = await client.get(
        "/api/agent-registry/p9_hr_agent/card",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    card = resp.json()
    assert "identity" in card
    assert "capabilities" in card
    assert card["identity"]["agent_id"] == "p9_hr_agent"
    assert len(card["capabilities"]) >= 1


# ── TC-9-07: Agent Card 직접 업데이트 ────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_agent_card(client, token, registered_agent):
    custom_card = {
        "identity": {"agent_id": "p9_hr_agent", "name": "HR Agent Custom"},
        "capabilities": [{"verb": "retrieve", "domain": "knowledge.hr"}],
        "version": {"card_schema_version": "2.0.0"},
    }
    resp = await client.put(
        "/api/agent-registry/p9_hr_agent/card",
        json={"agent_card_json": json.dumps(custom_card)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    # 이후 조회 시 업데이트된 Card 반환
    resp2 = await client.get(
        "/api/agent-registry/p9_hr_agent/card",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["identity"]["name"] == "HR Agent Custom"


# ── TC-9-08: Heartbeat 갱신 ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_heartbeat_updates_timestamp(client, token, registered_agent):
    resp = await client.post(
        "/api/agent-registry/p9_hr_agent/heartbeat",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent_key"] == "p9_hr_agent"
    assert data["lifecycle_state"] == "active"
    assert "lease_expires_at" in data


# ── TC-9-09: Heartbeat → quarantined 복구 ────────────────────────────────────

@pytest.mark.asyncio
async def test_heartbeat_recovers_from_quarantined(client, token, registered_agent):
    from app.db import _PH, execute_write

    # 강제로 quarantined 상태 설정
    await execute_write(
        f"UPDATE tbl_agent_registry SET lifecycle_state = 'quarantined' WHERE agent_key = {_PH}",
        ("p9_hr_agent",),
    )
    # heartbeat → active 복구
    resp = await client.post(
        "/api/agent-registry/p9_hr_agent/heartbeat",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["lifecycle_state"] == "active"


# ── TC-9-10: Health 조회 ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_health_status(client, token, registered_agent):
    # 먼저 heartbeat로 health_score 정상화
    await client.post(
        "/api/agent-registry/p9_hr_agent/heartbeat",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.get(
        "/api/agent-registry/p9_hr_agent/health",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent_key"] == "p9_hr_agent"
    assert "health_dot" in data
    assert "lifecycle_state" in data
    assert "lease_expired" in data
    assert data["health_dot"] == "green"
    assert data["lifecycle_state"] == "active"


# ── TC-9-11: Addon 업로드 → capabilities 저장 ────────────────────────────────

@pytest.mark.asyncio
async def test_upload_saves_capabilities(client, token):
    from app.db import _PH, fetch_all

    meta = {
        "agent_type": "service",
        "capabilities": [
            {"verb": "process", "domain": "service.test", "description": "테스트"},
        ],
    }
    zip_bytes = _make_zip("CapAgent", {
        "CapAgent-app.py": "from fastapi import APIRouter\nrouter = APIRouter()\n@router.get('/ping')\ndef ping(): return {'ok':True}\n",
        "CapAgent-meta.json": json.dumps(meta),
    })
    resp = await client.post(
        "/api/addon-agents/upload?force=true",
        files={"file": ("CapAgent.zip", zip_bytes, "application/zip")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    caps = await fetch_all(
        f"SELECT * FROM tbl_addon_agent_capabilities WHERE agent_key = {_PH}", ("capagent",)
    )
    assert len(caps) >= 1, f"capabilities 저장 안 됨: {caps}"
    assert caps[0]["verb"] == "process"
    assert caps[0]["domain"] == "service.test"

    # 정리
    await client.delete("/api/addon-agents/capagent", headers={"Authorization": f"Bearer {token}"})


# ── TC-9-12: 무효 Agent Card JSON → 400 ──────────────────────────────────────

@pytest.mark.asyncio
async def test_update_agent_card_invalid_json(client, token, registered_agent):
    resp = await client.put(
        "/api/agent-registry/p9_hr_agent/card",
        json={"agent_card_json": "not-valid-json{{{"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
