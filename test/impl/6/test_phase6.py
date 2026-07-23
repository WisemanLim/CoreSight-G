"""Phase 8 — MCP Proxy per-agent 통합 시험 (Iteration 6).

TC-6-01~16: tbl_mcp_configs CRUD, MCP status, MCP guide proxy_port, JSON-RPC.
"""
import os

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
    # Ensure dedicated test admin exists (isolated from live DB users)
    for uid, role, pw in [("p6_admin", "admin", "Admin6!"), ("p6_user", "user", "User6!")]:
        exists = await fetch_one(f"SELECT user_id FROM tbl_users WHERE user_id = {_PH}", (uid,))
        if not exists:
            await execute_write(
                f"INSERT INTO tbl_users (user_id, username, password, role) VALUES ({_PH},{_PH},{_PH},{_PH})",
                (uid, uid, hash_password(pw), role),
            )
    await addon_init(app)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    for uid in ("p6_admin", "p6_user"):
        await execute_write(f"DELETE FROM tbl_users WHERE user_id = {_PH}", (uid,))


@pytest_asyncio.fixture
async def token(client: AsyncClient) -> str:
    resp = await client.post("/api/auth/login", json={"user_id": "p6_admin", "password": "Admin6!"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def user_token(client: AsyncClient) -> str:
    """Regular user token for permission checks."""
    resp = await client.post("/api/auth/login", json={"user_id": "p6_user", "password": "User6!"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture(autouse=True)
async def cleanup():
    from app.db import _PH, execute_write
    await execute_write(
        f"DELETE FROM tbl_mcp_configs WHERE agent_key = {_PH}", ("board",)
    )
    yield
    await execute_write(
        f"DELETE FROM tbl_mcp_configs WHERE agent_key = {_PH}", ("board",)
    )


# ── TC-6-01: PUT upsert (생성) ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_config_upsert_create(client: AsyncClient, token: str):
    resp = await client.put(
        "/api/mcp-configs/board",
        json={"port": 20001, "extra_args": ["--header:x-api-key:tok"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["agent_key"] == "board"
    assert data["port"] == 20001
    assert data["extra_args"] == ["--header:x-api-key:tok"]
    assert data["is_enabled"] is True


# ── TC-6-02: GET 단건 ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_config_get_single(client: AsyncClient, token: str):
    # create first
    await client.put(
        "/api/mcp-configs/board",
        json={"port": 20001},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.get(
        "/api/mcp-configs/board",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["port"] == 20001


# ── TC-6-03: GET 목록 ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_config_list(client: AsyncClient, token: str):
    await client.put(
        "/api/mcp-configs/board",
        json={"port": 20001},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.get(
        "/api/mcp-configs/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    configs = resp.json()["configs"]
    keys = [c["agent_key"] for c in configs]
    assert "board" in keys


# ── TC-6-04: PUT upsert (갱신) ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_config_upsert_update(client: AsyncClient, token: str):
    await client.put(
        "/api/mcp-configs/board",
        json={"port": 20001, "extra_args": ["--header:x:y"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.put(
        "/api/mcp-configs/board",
        json={"port": 20002},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["port"] == 20002
    assert data["extra_args"] == []


# ── TC-6-05: DELETE ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_config_delete(client: AsyncClient, token: str):
    await client.put(
        "/api/mcp-configs/board",
        json={"port": 20001},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.delete(
        "/api/mcp-configs/board",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204
    # GET after delete → 404
    r2 = await client.get(
        "/api/mcp-configs/board",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 404


# ── TC-6-06: status — red (설정 없음) ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_status_red_no_config(client: AsyncClient, token: str):
    resp = await client.get(
        "/api/mcp-configs/board/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "red"


# ── TC-6-07: status — red (port 미설정) ← 버그 수정 검증 ────────────────────────

@pytest.mark.asyncio
async def test_mcp_status_red_no_port(client: AsyncClient, token: str):
    """port=null로 저장해도 red여야 한다 (green 오표시 버그 수정)."""
    await client.put(
        "/api/mcp-configs/board",
        json={"port": None, "is_enabled": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.get(
        "/api/mcp-configs/board/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "red", "port 없으면 red여야 함"


# ── TC-6-08: status — green (builtin, port 설정) ────────────────────────────────

_TC08_KEY = "p6_test_builtin"  # isolated key — not in tbl_addon_agents


@pytest.mark.asyncio
async def test_mcp_status_green_builtin(client: AsyncClient, token: str):
    """Builtin-only agent is_enabled=1 + port 설정 → green."""
    from app.db import _PH, execute_write
    # Insert a builtin-only agent not present in tbl_addon_agents
    await execute_write(
        f"INSERT OR IGNORE INTO tbl_agent_config (agent_key, agent_name, is_enabled, is_required) VALUES ({_PH},{_PH},1,0)",
        (_TC08_KEY, "P6 Test Builtin"),
    )
    await client.put(
        f"/api/mcp-configs/{_TC08_KEY}",
        json={"port": 20001},
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        resp = await client.get(
            f"/api/mcp-configs/{_TC08_KEY}/status",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "green"
    finally:
        await execute_write(f"DELETE FROM tbl_agent_config WHERE agent_key = {_PH}", (_TC08_KEY,))
        await execute_write(f"DELETE FROM tbl_mcp_configs WHERE agent_key = {_PH}", (_TC08_KEY,))


# ── TC-6-09: guide — proxy_port 반환 ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_guide_proxy_port(client: AsyncClient, token: str):
    await client.put(
        "/api/mcp-configs/board",
        json={"port": 20001},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.get("/mcp/board/guide")
    assert resp.status_code == 200
    data = resp.json()
    assert data["proxy_port"] == 20001
    assert "20001" in data["mcp_url"]
    assert data["mcp_url"].endswith("/mcp")


# ── TC-6-10: guide — proxy_port 미설정 시 자동 할당 ─────────────────────────────

@pytest.mark.asyncio
async def test_mcp_guide_no_proxy_port(client: AsyncClient):
    """proxy_port 미설정 시 guide가 20000-59999 범위 port 자동 할당 후 proxy URL 반환."""
    resp = await client.get("/mcp/board/guide")
    assert resp.status_code == 200
    data = resp.json()
    assert data["proxy_port"] is not None
    assert 20000 <= data["proxy_port"] <= 59999
    assert data["mcp_url"].endswith("/mcp")


# ── TC-6-11: status — DELETE 후 red ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_status_red_after_delete(client: AsyncClient, token: str):
    await client.put(
        "/api/mcp-configs/board",
        json={"port": 20001},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.delete(
        "/api/mcp-configs/board",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.get(
        "/api/mcp-configs/board/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.json()["status"] == "red"


# ── TC-6-12: JSON-RPC — tools/list builtin ───────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_jsonrpc_tools_list_builtin(client: AsyncClient, token: str):
    resp = await client.post(
        "/mcp/board",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data
    assert "tools" in data["result"]
    assert isinstance(data["result"]["tools"], list)


# ── TC-6-13: JSON-RPC — initialize ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_jsonrpc_initialize(client: AsyncClient, token: str):
    resp = await client.post(
        "/mcp/board",
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["protocolVersion"] == "2025-11-05"
    assert "board" in data["result"]["serverInfo"]["name"]


# ── TC-6-14: '0' 렌더링 버그 — 코드 패턴 검증 ────────────────────────────────────

@pytest.mark.asyncio
async def test_no_zero_rendering_pattern(client: AsyncClient):
    """AgentsPage에 !! 강제변환 패턴 존재 확인."""
    import os
    agents_page = os.path.join(
        os.path.dirname(__file__), "../../../front/src/pages/agents/AgentsPage.tsx"
    )
    with open(agents_page) as f:
        src = f.read()
    assert "!!c.is_enabled" in src, "builtin agent boolean coercion missing"
    assert "!!a.is_active" in src, "addon agent boolean coercion missing"


# ── TC-6-15: GET 404 — 없는 key ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_config_get_404(client: AsyncClient, token: str):
    resp = await client.get(
        "/api/mcp-configs/nonexistent_xyz_key",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


# ── TC-6-16: PUT — 권한 부족 (user role) ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_config_put_forbidden(client: AsyncClient, user_token: str):
    resp = await client.put(
        "/api/mcp-configs/board",
        json={"port": 20001},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 403
