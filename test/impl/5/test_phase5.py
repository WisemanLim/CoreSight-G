"""Phase 5 통합 시험 — F12 A2A Protocol · MCP JSON-RPC 2.0 · Agent Registry."""
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
    from app.db import apply_column_migrations, run_migrations, seed_default_admin
    await run_migrations()
    await apply_column_migrations()
    await seed_default_admin()
    await addon_init(app)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def token(client: AsyncClient) -> str:
    resp = await client.post("/api/auth/login", json={"user_id": "admin", "password": "Admin123!"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def viewer_token(client: AsyncClient, token: str) -> str:
    from app.db import _PH, fetch_one
    from app.core.security import hash_password
    exists = await fetch_one(f"SELECT user_id FROM tbl_users WHERE user_id = {_PH}", ("p5_viewer",))
    if not exists:
        await client.post(
            "/api/users/",
            json={"user_id": "p5_viewer", "username": "V", "password": "View123!", "role": "viewer"},
            headers={"Authorization": f"Bearer {token}"},
        )
    resp = await client.post("/api/auth/login", json={"user_id": "p5_viewer", "password": "View123!"})
    return resp.json()["access_token"]


@pytest_asyncio.fixture(autouse=True)
async def cleanup_registry():
    from app.db import _PH, execute_write
    await execute_write(
        f"DELETE FROM tbl_agent_registry WHERE agent_key = {_PH}", ("remote_test",)
    )
    yield
    await execute_write(
        f"DELETE FROM tbl_agent_registry WHERE agent_key = {_PH}", ("remote_test",)
    )


def _mcp(method: str, params: dict | None = None, id_: int = 1) -> dict:
    return {"jsonrpc": "2.0", "id": id_, "method": method, "params": params or {}}


# ── MCP tests ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t1_mcp_initialize(client: AsyncClient):
    """T1: MCP initialize → protocolVersion + capabilities."""
    resp = await client.post("/mcp", json=_mcp("initialize"))
    assert resp.status_code == 200
    result = resp.json()["result"]
    assert result["protocolVersion"] == "2025-11-05"
    assert "capabilities" in result
    assert "tools" in result["capabilities"]


@pytest.mark.asyncio
async def test_t2_mcp_tools_list(client: AsyncClient):
    """T2: tools/list → ExampleAgent 도구 목록."""
    resp = await client.post("/mcp", json=_mcp("tools/list"))
    assert resp.status_code == 200
    tools = resp.json()["result"]["tools"]
    assert isinstance(tools, list)
    assert len(tools) >= 1
    assert "name" in tools[0]
    assert "inputSchema" in tools[0]


@pytest.mark.asyncio
async def test_t3_mcp_tools_call(client: AsyncClient):
    """T3: tools/call → content[0].type = text."""
    resp = await client.post("/mcp", json=_mcp(
        "tools/call",
        {"name": "get_example_data", "arguments": {"query": "test"}}
    ))
    assert resp.status_code == 200
    body = resp.json()
    assert "result" in body
    content = body["result"]["content"]
    assert content[0]["type"] == "text"


@pytest.mark.asyncio
async def test_t4_mcp_tools_call_unknown(client: AsyncClient):
    """T4: 존재하지 않는 tool → error.code = -32602."""
    resp = await client.post("/mcp", json=_mcp(
        "tools/call", {"name": "nonexistent_tool", "arguments": {}}
    ))
    assert resp.status_code == 200
    assert resp.json()["error"]["code"] == -32602


@pytest.mark.asyncio
async def test_t5_mcp_resources_list(client: AsyncClient):
    """T5: resources/list → domain://context 리소스."""
    resp = await client.post("/mcp", json=_mcp("resources/list"))
    assert resp.status_code == 200
    resources = resp.json()["result"]["resources"]
    assert any(r["uri"] == "domain://context" for r in resources)


@pytest.mark.asyncio
async def test_t6_mcp_resources_read(client: AsyncClient):
    """T6: resources/read domain://context → contents[0].uri 일치."""
    resp = await client.post("/mcp", json=_mcp("resources/read", {"uri": "domain://context"}))
    assert resp.status_code == 200
    contents = resp.json()["result"]["contents"]
    assert contents[0]["uri"] == "domain://context"


@pytest.mark.asyncio
async def test_t7_mcp_prompts(client: AsyncClient):
    """T7: prompts/list + prompts/get → system prompt 반환."""
    resp_list = await client.post("/mcp", json=_mcp("prompts/list"))
    prompts = resp_list.json()["result"]["prompts"]
    assert any(p["name"] == "system" for p in prompts)

    resp_get = await client.post("/mcp", json=_mcp("prompts/get", {"name": "system"}))
    messages = resp_get.json()["result"]["messages"]
    assert messages[0]["role"] == "user"


@pytest.mark.asyncio
async def test_t8_mcp_unknown_method(client: AsyncClient):
    """T8: 존재하지 않는 method → error.code = -32601."""
    resp = await client.post("/mcp", json=_mcp("nonexistent/method"))
    assert resp.status_code == 200
    assert resp.json()["error"]["code"] == -32601


# ── A2A tests ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t9_agent_card(client: AsyncClient):
    """T9: AgentCard — 인증 불필요, capabilities.streaming = true."""
    resp = await client.get("/.well-known/agent-card.json")
    assert resp.status_code == 200
    card = resp.json()
    assert card["capabilities"]["streaming"] is True
    assert isinstance(card["skills"], list)
    assert "authentication" in card


@pytest.mark.asyncio
async def test_t10_a2a_create_task(client: AsyncClient, token: str):
    """T10: POST /a2a/tasks → 201, task_id + status=submitted."""
    resp = await client.post(
        "/a2a/tasks",
        json={"message": {"role": "user", "parts": [{"kind": "text", "text": "안녕"}]}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["status"] == "submitted"


@pytest.mark.asyncio
async def test_t11_a2a_task_result(client: AsyncClient, token: str):
    """T11: GET /a2a/tasks/{id}/result → 200, id 일치."""
    create = await client.post(
        "/a2a/tasks",
        json={"message": {"role": "user", "parts": [{"kind": "text", "text": "test"}]}},
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = create.json()["id"]

    resp = await client.get(
        f"/a2a/tasks/{task_id}/result",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == task_id


@pytest.mark.asyncio
async def test_t12_a2a_task_not_found(client: AsyncClient, token: str):
    """T12: 없는 task_id → 404."""
    resp = await client.get(
        "/a2a/tasks/00000000-0000-0000-0000-000000000000/result",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


# ── Agent Registry tests ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t13_registry_list_empty(client: AsyncClient, token: str):
    """T13: 빈 Registry → agents 배열 반환."""
    resp = await client.get("/api/agent-registry/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "agents" in resp.json()


@pytest.mark.asyncio
async def test_t14_registry_register(client: AsyncClient, token: str):
    """T14: 외부 Agent 등록 → 201."""
    resp = await client.post(
        "/api/agent-registry/",
        json={
            "agent_key": "remote_test",
            "agent_name": "Remote Test Agent",
            "protocol": "a2a",
            "agent_card_url": "http://localhost:9999/.well-known/agent-card.json",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["agent_key"] == "remote_test"


@pytest.mark.asyncio
async def test_t15_registry_duplicate_409(client: AsyncClient, token: str):
    """T15: 중복 agent_key → 409."""
    payload = {"agent_key": "remote_test", "agent_name": "X", "protocol": "a2a"}
    await client.post("/api/agent-registry/", json=payload, headers={"Authorization": f"Bearer {token}"})
    resp = await client.post("/api/agent-registry/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_t16_registry_list_shows_entry(client: AsyncClient, token: str):
    """T16: 등록 후 목록에 포함."""
    await client.post(
        "/api/agent-registry/",
        json={"agent_key": "remote_test", "agent_name": "R", "protocol": "a2a"},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.get("/api/agent-registry/", headers={"Authorization": f"Bearer {token}"})
    keys = [a["agent_key"] for a in resp.json()["agents"]]
    assert "remote_test" in keys


@pytest.mark.asyncio
async def test_t17_registry_ping_no_url(client: AsyncClient, token: str):
    """T17: URL 없는 Agent ping → ok=False."""
    await client.post(
        "/api/agent-registry/",
        json={"agent_key": "remote_test", "agent_name": "R", "protocol": "a2a"},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.post(
        "/api/agent-registry/remote_test/ping",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is False


@pytest.mark.asyncio
async def test_t18_registry_delete(client: AsyncClient, token: str):
    """T18: 등록 후 삭제 → 200."""
    await client.post(
        "/api/agent-registry/",
        json={"agent_key": "remote_test", "agent_name": "R", "protocol": "a2a"},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.delete(
        "/api/agent-registry/remote_test",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_t19_registry_viewer_403(client: AsyncClient, viewer_token: str):
    """T19: viewer 권한 Registry 접근 → 403."""
    resp = await client.get("/api/agent-registry/", headers={"Authorization": f"Bearer {viewer_token}"})
    assert resp.status_code == 403
