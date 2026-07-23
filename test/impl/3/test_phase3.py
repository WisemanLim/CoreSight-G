"""Phase 3 통합 시험 — Setup Wizard · Agent Config · Addon Agent."""
import io
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
    # lifespan 이 테스트에서 자동 실행되지 않으므로 수동으로 초기화
    from app.addon_agent_loader import init as addon_init
    from app.db import apply_column_migrations, run_migrations, seed_default_admin
    await run_migrations()
    await apply_column_migrations()
    await seed_default_admin()
    await addon_init(app)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient) -> str:
    resp = await client.post("/api/auth/login", json={"user_id": "admin", "password": "Admin123!"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def viewer_token(client: AsyncClient) -> str:
    """viewer 권한 사용자 토큰 — 없으면 생성."""
    from app.db import _PH, execute_write, fetch_one
    from app.core.security import hash_password
    user = await fetch_one(f"SELECT user_id FROM tbl_users WHERE user_id = {_PH}", ("viewer_test",))
    if not user:
        await execute_write(
            f"INSERT INTO tbl_users (user_id, username, password, role) VALUES ({_PH},{_PH},{_PH},{_PH})",
            ("viewer_test", "viewer_test", hash_password("Viewer123!"), "viewer"),
        )
    resp = await client.post("/api/auth/login", json={"user_id": "viewer_test", "password": "Viewer123!"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _make_example_zip() -> bytes:
    """ExampleAddon.zip 인메모리 생성."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "ExampleAddon-app.py",
            "from fastapi import APIRouter\nrouter = APIRouter()\n\n"
            "@router.get('/items')\nasync def list_items():\n    return {'items': [], 'note': 'test'}\n",
        )
    return buf.getvalue()


def _make_malicious_zip() -> bytes:
    """'..' 경로 포함 ZIP."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../evil.py", "# pwned")
    return buf.getvalue()


@pytest_asyncio.fixture(autouse=True)
async def cleanup_addon():
    """각 테스트 전후 exampleaddon 정리."""
    from app.db import _PH, execute_write
    await execute_write("DELETE FROM tbl_addon_agents WHERE agent_key = ?", ("exampleaddon",))
    await execute_write("DELETE FROM tbl_agent_config WHERE agent_key = ?", ("exampleaddon",))
    import shutil, pathlib
    shutil.rmtree(pathlib.Path("addon-agents/deployed/exampleaddon"), ignore_errors=True)
    yield
    await execute_write("DELETE FROM tbl_addon_agents WHERE agent_key = ?", ("exampleaddon",))
    await execute_write("DELETE FROM tbl_agent_config WHERE agent_key = ?", ("exampleaddon",))
    shutil.rmtree(pathlib.Path("addon-agents/deployed/exampleaddon"), ignore_errors=True)


@pytest_asyncio.fixture(autouse=True)
async def cleanup_viewer_user():
    """viewer_test 사용자 정리."""
    yield
    from app.db import _PH, execute_write
    await execute_write("DELETE FROM tbl_users WHERE user_id = ?", ("viewer_test",))


# ── T1-T5: Setup Wizard ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t1_setup_status_initial(client: AsyncClient):
    """T1: 초기 상태 — has_supervisor=true, completed 확인."""
    resp = await client.get("/api/setup/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_supervisor"] is True  # default admin exists


@pytest.mark.asyncio
async def test_t2_create_supervisor_duplicate(client: AsyncClient):
    """T2: supervisor 이미 존재 → 409."""
    resp = await client.post("/api/setup/supervisor", json={
        "user_id": "super2", "username": "super2", "password": "Super123!"
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_t3_llm_provider(client: AsyncClient):
    """T3: LLM Provider 설정 저장 → 200."""
    resp = await client.put("/api/setup/llm-provider", json={
        "orchestrator_model": "claude-sonnet-4-6",
        "domain_agent_model": "claude-haiku-4-5-20251001",
        "ollama_base_url": "http://localhost:11434",
        "ollama_model": "llama3.2",
        "fallback_enabled": True,
    })
    assert resp.status_code == 200
    assert "saved" in resp.json()["message"]


@pytest.mark.asyncio
async def test_t4_setup_complete(client: AsyncClient):
    """T4: Setup 완료 마킹 → 200."""
    resp = await client.post("/api/setup/complete")
    assert resp.status_code == 200
    assert resp.json().get("setup_completed") is True


@pytest.mark.asyncio
async def test_t5_setup_status_after_complete(client: AsyncClient):
    """T5: complete 후 status → completed=true."""
    await client.post("/api/setup/complete")
    resp = await client.get("/api/setup/status")
    assert resp.status_code == 200
    assert resp.json()["completed"] is True


# ── T6-T9: Agent Config ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t6_list_agent_config(client: AsyncClient, admin_token: str):
    """T6: Agent Config 목록 — example 포함."""
    resp = await client.get("/api/agent-config/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    agents = resp.json()["agents"]
    assert any(a["agent_key"] == "example" for a in agents)


@pytest.mark.asyncio
async def test_t7_patch_agent_disable(client: AsyncClient, admin_token: str):
    """T7: example Agent 비활성화 → 200."""
    resp = await client.patch(
        "/api/agent-config/example",
        json={"is_enabled": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_t8_get_agent_disabled(client: AsyncClient, admin_token: str):
    """T8: 비활성화된 example 조회 → is_enabled=0."""
    await client.patch(
        "/api/agent-config/example",
        json={"is_enabled": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.get(
        "/api/agent-config/example",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_enabled"] == 0


@pytest.mark.asyncio
async def test_t9_patch_agent_reenable(client: AsyncClient, admin_token: str):
    """T9: example Agent 재활성화 → 200."""
    await client.patch(
        "/api/agent-config/example",
        json={"is_enabled": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.patch(
        "/api/agent-config/example",
        json={"is_enabled": True},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200

    get_resp = await client.get(
        "/api/agent-config/example",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert get_resp.json()["is_enabled"] == 1


# ── T10-T18: Addon Agent ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t10_list_addons_empty(client: AsyncClient, admin_token: str):
    """T10: 초기 addon 목록 — 빈 배열."""
    resp = await client.get("/api/addon-agents/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["addons"] == []


@pytest.mark.asyncio
async def test_t11_upload_addon(client: AsyncClient, admin_token: str):
    """T11: ExampleAddon.zip 업로드 → 200, api_prefix 반환."""
    resp = await client.post(
        "/api/addon-agents/upload",
        files={"file": ("ExampleAddon.zip", _make_example_zip(), "application/zip")},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["agent_key"] == "exampleaddon"
    assert data["api_prefix"] == "/api/addon/exampleaddon"


@pytest.mark.asyncio
async def test_t12_list_addons_after_upload(client: AsyncClient, admin_token: str):
    """T12: 업로드 후 addon 목록 — 1건."""
    await client.post(
        "/api/addon-agents/upload",
        files={"file": ("ExampleAddon.zip", _make_example_zip(), "application/zip")},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.get("/api/addon-agents/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert len(resp.json()["addons"]) == 1


@pytest.mark.asyncio
async def test_t13_hot_loaded_route(client: AsyncClient, admin_token: str):
    """T13: 핫 로드된 /api/addon/exampleaddon/items → 200."""
    upload = await client.post(
        "/api/addon-agents/upload",
        files={"file": ("ExampleAddon.zip", _make_example_zip(), "application/zip")},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert upload.status_code == 200, upload.text

    resp = await client.get(
        "/api/addon/exampleaddon/items",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert "items" in resp.json()


@pytest.mark.asyncio
async def test_t14_upload_duplicate_no_force(client: AsyncClient, admin_token: str):
    """T14: 중복 업로드 force=false → 409."""
    zip_data = _make_example_zip()
    await client.post(
        "/api/addon-agents/upload",
        files={"file": ("ExampleAddon.zip", zip_data, "application/zip")},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.post(
        "/api/addon-agents/upload",
        files={"file": ("ExampleAddon.zip", zip_data, "application/zip")},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_t15_delete_addon(client: AsyncClient, admin_token: str):
    """T15: addon 삭제 → 200."""
    await client.post(
        "/api/addon-agents/upload",
        files={"file": ("ExampleAddon.zip", _make_example_zip(), "application/zip")},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.delete(
        "/api/addon-agents/exampleaddon",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_t16_list_addons_after_delete(client: AsyncClient, admin_token: str):
    """T16: 삭제 후 addon 목록 — 빈 배열."""
    await client.post(
        "/api/addon-agents/upload",
        files={"file": ("ExampleAddon.zip", _make_example_zip(), "application/zip")},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    await client.delete(
        "/api/addon-agents/exampleaddon",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.get("/api/addon-agents/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.json()["addons"] == []


@pytest.mark.asyncio
async def test_t17_upload_viewer_forbidden(client: AsyncClient, viewer_token: str):
    """T17: viewer 권한으로 업로드 → 403."""
    resp = await client.post(
        "/api/addon-agents/upload",
        files={"file": ("ExampleAddon.zip", _make_example_zip(), "application/zip")},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_t18_upload_path_traversal(client: AsyncClient, admin_token: str):
    """T18: '..' 경로 포함 ZIP → 400."""
    resp = await client.post(
        "/api/addon-agents/upload",
        files={"file": ("ExampleAddon.zip", _make_malicious_zip(), "application/zip")},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 400
