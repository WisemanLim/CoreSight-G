"""Phase 4 통합 시험 — 사용자 관리 · 설정 · Setup Wizard 멱등 · Frontend 빌드."""
import os
import subprocess
from pathlib import Path

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
async def sup_token(client: AsyncClient) -> str:
    resp = await client.post("/api/auth/login", json={"user_id": "admin", "password": "Admin123!"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient, sup_token: str) -> str:
    """admin 역할 사용자 생성 후 토큰 반환."""
    from app.db import _PH, fetch_one
    existing = await fetch_one(f"SELECT user_id FROM tbl_users WHERE user_id = {_PH}", ("p4_admin",))
    if not existing:
        await client.post(
            "/api/users/",
            json={"user_id": "p4_admin", "username": "Phase4Admin", "password": "Admin123!", "role": "admin"},
            headers={"Authorization": f"Bearer {sup_token}"},
        )
    resp = await client.post("/api/auth/login", json={"user_id": "p4_admin", "password": "Admin123!"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def viewer_token(client: AsyncClient, sup_token: str) -> str:
    from app.db import _PH, fetch_one
    existing = await fetch_one(f"SELECT user_id FROM tbl_users WHERE user_id = {_PH}", ("p4_viewer",))
    if not existing:
        await client.post(
            "/api/users/",
            json={"user_id": "p4_viewer", "username": "Phase4Viewer", "password": "View123!", "role": "viewer"},
            headers={"Authorization": f"Bearer {sup_token}"},
        )
    resp = await client.post("/api/auth/login", json={"user_id": "p4_viewer", "password": "View123!"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture(autouse=True)
async def cleanup_test_user():
    """각 테스트 전후 u4_test 사용자 정리."""
    from app.db import _PH, execute_write
    await execute_write(f"DELETE FROM tbl_users WHERE user_id = {_PH}", ("u4_test",))
    yield
    await execute_write(f"DELETE FROM tbl_users WHERE user_id = {_PH}", ("u4_test",))


# ── T1: Setup 상태 ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t1_setup_status_with_supervisor(client: AsyncClient):
    """T1: supervisor 존재 시 has_supervisor=true."""
    resp = await client.get("/api/setup/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_supervisor"] is True
    assert "completed" in data


# ── T2-T9: 사용자 관리 API ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t2_list_users_supervisor(client: AsyncClient, sup_token: str):
    """T2: supervisor → 사용자 목록 조회."""
    resp = await client.get("/api/users/", headers={"Authorization": f"Bearer {sup_token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert "users" in body
    assert "total" in body
    assert body["total"] >= 1


@pytest.mark.asyncio
async def test_t3_create_user(client: AsyncClient, sup_token: str):
    """T3: supervisor → 사용자 생성 201."""
    resp = await client.post(
        "/api/users/",
        json={"user_id": "u4_test", "username": "테스트유저", "password": "Test123!", "role": "user"},
        headers={"Authorization": f"Bearer {sup_token}"},
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_t4_user_appears_in_list(client: AsyncClient, sup_token: str):
    """T4: 생성된 사용자가 목록에 포함."""
    await client.post(
        "/api/users/",
        json={"user_id": "u4_test", "username": "테스트", "password": "Test123!", "role": "user"},
        headers={"Authorization": f"Bearer {sup_token}"},
    )
    resp = await client.get("/api/users/", headers={"Authorization": f"Bearer {sup_token}"})
    ids = [u["user_id"] for u in resp.json()["users"]]
    assert "u4_test" in ids


@pytest.mark.asyncio
async def test_t5_duplicate_user_409(client: AsyncClient, sup_token: str):
    """T5: 중복 user_id → 409."""
    payload = {"user_id": "u4_test", "username": "X", "password": "Test123!", "role": "user"}
    await client.post("/api/users/", json=payload, headers={"Authorization": f"Bearer {sup_token}"})
    resp = await client.post("/api/users/", json=payload, headers={"Authorization": f"Bearer {sup_token}"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_t6_list_users_no_auth_401(client: AsyncClient):
    """T6: 비인증 → 401."""
    resp = await client.get("/api/users/")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_t7_list_users_viewer_403(client: AsyncClient, viewer_token: str):
    """T7: viewer → 사용자 목록 403."""
    resp = await client.get("/api/users/", headers={"Authorization": f"Bearer {viewer_token}"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_t8_delete_user_by_admin_403(client: AsyncClient, sup_token: str, admin_token: str):
    """T8: admin 역할은 삭제 불가 → 403."""
    await client.post(
        "/api/users/",
        json={"user_id": "u4_test", "username": "X", "password": "Test123!", "role": "user"},
        headers={"Authorization": f"Bearer {sup_token}"},
    )
    resp = await client.delete("/api/users/u4_test", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_t9_delete_user_by_supervisor(client: AsyncClient, sup_token: str):
    """T9: supervisor → 사용자 삭제 200."""
    await client.post(
        "/api/users/",
        json={"user_id": "u4_test", "username": "X", "password": "Test123!", "role": "user"},
        headers={"Authorization": f"Bearer {sup_token}"},
    )
    resp = await client.delete("/api/users/u4_test", headers={"Authorization": f"Bearer {sup_token}"})
    assert resp.status_code == 200


# ── T10-T13: 시스템 설정 API ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t10_get_settings(client: AsyncClient, sup_token: str):
    """T10: 설정 목록 조회 — settings 배열 반환."""
    resp = await client.get("/api/settings/", headers={"Authorization": f"Bearer {sup_token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert "settings" in body
    assert isinstance(body["settings"], list)


@pytest.mark.asyncio
async def test_t11_update_setting(client: AsyncClient, sup_token: str):
    """T11: 설정 변경 200."""
    resp = await client.put(
        "/api/settings/ollama_model",
        json={"value": "llama3.2-test", "description": "test"},
        headers={"Authorization": f"Bearer {sup_token}"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_t12_updated_value_visible(client: AsyncClient, sup_token: str):
    """T12: 변경 후 조회 시 값 반영."""
    await client.put(
        "/api/settings/ollama_model",
        json={"value": "llama3.2-test", "description": "test"},
        headers={"Authorization": f"Bearer {sup_token}"},
    )
    resp = await client.get("/api/settings/", headers={"Authorization": f"Bearer {sup_token}"})
    settings = {s["key"]: s["value"] for s in resp.json()["settings"]}
    assert settings.get("ollama_model") == "llama3.2-test"


@pytest.mark.asyncio
async def test_t13_test_llm_endpoint(client: AsyncClient, sup_token: str):
    """T13: LLM 테스트 엔드포인트 — ollama/anthropic 상태 반환."""
    resp = await client.post("/api/settings/test-llm", headers={"Authorization": f"Bearer {sup_token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert "ollama" in body
    assert "anthropic_configured" in body


# ── T14-T17: Setup Wizard 멱등 확인 ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_t14_setup_supervisor_duplicate_409(client: AsyncClient):
    """T14: supervisor 이미 존재 → POST /api/setup/supervisor 409."""
    resp = await client.post(
        "/api/setup/supervisor",
        json={"user_id": "another_sv", "username": "X", "password": "X12345678!"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_t15_setup_llm_provider_idempotent(client: AsyncClient):
    """T15: PUT /api/setup/llm-provider 인증 불필요, 멱등."""
    resp = await client.put(
        "/api/setup/llm-provider",
        json={
            "orchestrator_model": "claude-sonnet-4-6",
            "domain_agent_model": "claude-haiku-4-5-20251001",
            "ollama_base_url": "http://localhost:11434",
            "ollama_model": "llama3.2",
            "fallback_enabled": True,
        },
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_t16_setup_complete_idempotent(client: AsyncClient):
    """T16: POST /api/setup/complete 멱등."""
    resp = await client.post("/api/setup/complete")
    assert resp.status_code == 200
    assert resp.json()["setup_completed"] is True


@pytest.mark.asyncio
async def test_t17_setup_status_after_complete(client: AsyncClient):
    """T17: 완료 후 status → completed=true."""
    await client.post("/api/setup/complete")
    resp = await client.get("/api/setup/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_supervisor"] is True
    assert data["completed"] is True


# ── T18: 프론트엔드 빌드 검증 ─────────────────────────────────────────────────

def test_t18_frontend_build():
    """T18: pnpm build — TypeScript 타입 검증 + Vite 빌드."""
    front_dir = Path(__file__).parents[3] / "front"
    result = subprocess.run(
        ["pnpm", "build"],
        cwd=front_dir,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"pnpm build failed:\n{result.stdout}\n{result.stderr}"
