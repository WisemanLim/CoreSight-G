"""Phase 1 통합 시험 — 인증·사용자·설정."""
import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("ENV", "local")

from app.main import app  # noqa: E402


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient) -> str:
    resp = await client.post("/api/auth/login", json={"user_id": "admin", "password": "Admin123!"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


# ── T1: DB seed ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t1_admin_exists(client: AsyncClient, admin_token: str):
    """T1: 기본 관리자 계정이 DB 에 존재해야 한다."""
    resp = await client.get("/api/users/", headers={"Authorization": f"Bearer {admin_token}"})
    users = resp.json()["users"]
    assert any(u["user_id"] == "admin" for u in users)


# ── T2-T4: 로그인 ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t2_login_success(client: AsyncClient):
    """T2: 정상 로그인 → 200 + access_token."""
    resp = await client.post("/api/auth/login", json={"user_id": "admin", "password": "Admin123!"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["role"] == "supervisor"


@pytest.mark.asyncio
async def test_t3_login_wrong_password(client: AsyncClient):
    """T3: 잘못된 비밀번호 → 401."""
    resp = await client.post("/api/auth/login", json={"user_id": "admin", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_t4_login_unknown_user(client: AsyncClient):
    """T4: 없는 사용자 → 401."""
    resp = await client.post("/api/auth/login", json={"user_id": "nobody", "password": "x"})
    assert resp.status_code == 401


# ── T5-T8: 사용자 관리 ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t5_users_no_auth(client: AsyncClient):
    """T5: 인증 없이 /api/users/ → 401 또는 403."""
    resp = await client.get("/api/users/")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_t6_list_users(client: AsyncClient, admin_token: str):
    """T6: supervisor 토큰으로 목록 조회 → 200."""
    resp = await client.get("/api/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert "users" in resp.json()


@pytest_asyncio.fixture
async def clean_pytest_user():
    """T7/T8 용: 테스트 전후 pytest_user 정리."""
    from app.db import _PH, execute_write
    await execute_write(f"DELETE FROM tbl_users WHERE user_id = {_PH}", ("pytest_user",))
    yield
    await execute_write(f"DELETE FROM tbl_users WHERE user_id = {_PH}", ("pytest_user",))


@pytest.mark.asyncio
async def test_t7_create_and_t8_duplicate(client: AsyncClient, admin_token: str, clean_pytest_user):
    """T7: 새 사용자 생성 → 201. T8: 중복 → 409."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"user_id": "pytest_user", "username": "pytest", "password": "Test123!", "role": "user"}

    resp = await client.post("/api/users/", json=payload, headers=headers)
    assert resp.status_code == 201

    resp2 = await client.post("/api/users/", json=payload, headers=headers)
    assert resp2.status_code == 409


# ── T9: 설정 조회 ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t9_get_settings(client: AsyncClient, admin_token: str):
    """T9: 설정 목록 조회 → 200, 목록 포함."""
    resp = await client.get("/api/settings/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json()["settings"], list)


# ── T10: 로그아웃 후 토큰 무효화 ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t10_logout_revokes_token(client: AsyncClient):
    """T10: 로그아웃 후 동일 토큰 재사용 → 401."""
    login = await client.post("/api/auth/login", json={"user_id": "admin", "password": "Admin123!"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout = await client.post("/api/auth/logout", headers=headers)
    assert logout.status_code == 200

    resp = await client.get("/api/users/", headers=headers)
    assert resp.status_code == 401
