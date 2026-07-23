"""Phase 8 — MCP server_host + proxy URL 통합 시험 (Iteration 7).

TC-7-01~07: server_host 필드, proxy_port URL 형식, 회귀 검증.
"""
import os
import re

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
    for uid, role, pw in [("p7_admin", "admin", "Admin7!")]:
        exists = await fetch_one(f"SELECT user_id FROM tbl_users WHERE user_id = {_PH}", (uid,))
        if not exists:
            await execute_write(
                f"INSERT INTO tbl_users (user_id, username, password, role) VALUES ({_PH},{_PH},{_PH},{_PH})",
                (uid, uid, hash_password(pw), role),
            )
    await addon_init(app)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    await execute_write(f"DELETE FROM tbl_users WHERE user_id = {_PH}", ("p7_admin",))


@pytest_asyncio.fixture
async def token(client: AsyncClient) -> str:
    resp = await client.post("/api/auth/login", json={"user_id": "p7_admin", "password": "Admin7!"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture(autouse=True)
async def cleanup():
    from app.db import _PH, execute_write
    await execute_write(f"DELETE FROM tbl_mcp_configs WHERE agent_key = {_PH}", ("board",))
    yield
    await execute_write(f"DELETE FROM tbl_mcp_configs WHERE agent_key = {_PH}", ("board",))


# ── TC-7-01: guide에 server_host 필드 존재 ───────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_guide_has_server_host(client: AsyncClient, token: str):
    """guide 응답에 server_host 키가 있어야 한다."""
    await client.put(
        "/api/mcp-configs/board",
        json={"port": 20001},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.get("/mcp/board/guide")
    assert resp.status_code == 200
    data = resp.json()
    assert "server_host" in data, "server_host 필드 누락"
    assert data["server_host"] is not None
    assert data["server_host"] != ""


# ── TC-7-02: proxy_port 시 mcp_url = http://{server_host}:{port}/mcp ─────────

@pytest.mark.asyncio
async def test_mcp_guide_proxy_url_format(client: AsyncClient, token: str):
    """proxy_port 설정 시 mcp_url = http://{server_host}:{port}/mcp 형식."""
    await client.put(
        "/api/mcp-configs/board",
        json={"port": 20001},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.get("/mcp/board/guide")
    assert resp.status_code == 200
    data = resp.json()
    server_host = data["server_host"]
    assert data["mcp_url"] == f"http://{server_host}:20001/mcp", (
        f"Expected http://{server_host}:20001/mcp, got {data['mcp_url']}"
    )


# ── TC-7-03: proxy_port 없을 때 guide가 자동 할당 후 http://{server_host}:{port}/mcp ──

@pytest.mark.asyncio
async def test_mcp_guide_no_proxy_url_format(client: AsyncClient):
    """proxy_port 미설정 → guide 자동 할당 후 http://{server_host}:{port}/mcp 반환."""
    resp = await client.get("/mcp/board/guide")
    assert resp.status_code == 200
    data = resp.json()
    server_host = data["server_host"]
    assert server_host in data["mcp_url"], f"server_host({server_host}) not in mcp_url({data['mcp_url']})"
    assert data["mcp_url"].endswith("/mcp")
    assert data["proxy_port"] is not None


# ── TC-7-04: server_host는 유효한 IP 또는 hostname ────────────────────────────

@pytest.mark.asyncio
async def test_mcp_guide_server_host_valid(client: AsyncClient):
    """server_host는 빈값이 아니며 유효한 IP/hostname 형식."""
    resp = await client.get("/mcp/board/guide")
    assert resp.status_code == 200
    data = resp.json()
    sh = data.get("server_host", "")
    assert sh, "server_host is empty"
    # IP(x.x.x.x) 또는 hostname(영숫자/하이픈)
    is_ip = bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", sh))
    is_hostname = bool(re.match(r"^[a-zA-Z0-9._-]+$", sh))
    assert is_ip or is_hostname, f"server_host invalid: {sh}"


# ── TC-7-05: proxy_port 시 mcp_url이 localhost 미포함 (server_host가 실IP일 때) ─

@pytest.mark.asyncio
async def test_mcp_guide_proxy_url_no_localhost_when_real_ip(client: AsyncClient, token: str):
    """server_host가 실제 IP(127.0.0.1/localhost 아님)이면 mcp_url에 localhost 없어야 함."""
    await client.put(
        "/api/mcp-configs/board",
        json={"port": 20001},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.get("/mcp/board/guide")
    assert resp.status_code == 200
    data = resp.json()
    sh = data["server_host"]
    if sh not in ("localhost", "127.0.0.1"):
        assert "localhost" not in data["mcp_url"], (
            f"server_host={sh} is real IP but mcp_url contains localhost: {data['mcp_url']}"
        )


# ── TC-7-06: 회귀 — proxy_port=20001 → "20001" in mcp_url + endswith /mcp ────

@pytest.mark.asyncio
async def test_mcp_guide_proxy_port_regression(client: AsyncClient, token: str):
    """TC-6-09 회귀: proxy_port=20001 → mcp_url에 20001 포함 + /mcp 종료."""
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


# ── TC-7-07: proxy_port 미설정 시 auto-assign → proxy URL 형식 반환 ─────────────

@pytest.mark.asyncio
async def test_mcp_guide_no_proxy_regression(client: AsyncClient):
    """proxy_port 미설정 시 guide auto-assign → proxy URL (TC-6-10 행동 업데이트)."""
    resp = await client.get("/mcp/board/guide")
    assert resp.status_code == 200
    data = resp.json()
    assert data["proxy_port"] is not None
    assert 20000 <= data["proxy_port"] <= 59999
    assert data["mcp_url"].endswith("/mcp")
