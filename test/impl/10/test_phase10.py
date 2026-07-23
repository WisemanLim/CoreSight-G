"""Phase 11 — F24 Agent Builder UI 통합 시험 (Iteration 10).

TC-10-01~12: scaffold API 9종 + 유효성 검사 + ZIP 내용 검증 + TS 빌드.
"""
import io
import json
import os
import subprocess
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

    uid, pw = "p10_admin", "Admin10!"
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


@pytest_asyncio.fixture
async def token(client):
    resp = await client.post("/api/auth/login", json={"user_id": "p10_admin", "password": "Admin10!"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _zip_files(content: bytes) -> set[str]:
    buf = io.BytesIO(content)
    with zipfile.ZipFile(buf) as zf:
        return set(zf.namelist())


def _zip_read(content: bytes, filename: str) -> str:
    buf = io.BytesIO(content)
    with zipfile.ZipFile(buf) as zf:
        return zf.read(filename).decode("utf-8")


# ── TC-10-01: app 유형 scaffold ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_scaffold_app_type(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "TestApp", "agent_type": "app", "description": "테스트 앱"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"
    files = _zip_files(resp.content)
    assert any("TestApp" in f for f in files)


# ── TC-10-02: service 유형 scaffold ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_scaffold_service_type(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "TestService", "agent_type": "service"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    files = _zip_files(resp.content)
    assert "TestService-app.py" in files


# ── TC-10-03: rag 유형 scaffold ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_scaffold_rag_type(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "TestRag", "agent_type": "rag"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    files = _zip_files(resp.content)
    assert "TestRag-app.py" in files


# ── TC-10-04: tool-proxy 유형 scaffold ───────────────────────────────────────

@pytest.mark.asyncio
async def test_scaffold_tool_proxy_type(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "TestProxy", "agent_type": "tool-proxy"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    files = _zip_files(resp.content)
    assert "TestProxy-app.py" in files


# ── TC-10-05: reviewer 유형 scaffold (템플릿 없음 → 기본 구조) ──────────────────

@pytest.mark.asyncio
async def test_scaffold_reviewer_type_fallback(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "TestReviewer", "agent_type": "reviewer"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"
    files = _zip_files(resp.content)
    assert any("TestReviewer" in f for f in files)


# ── TC-10-06: 이름 유효성 — 숫자 시작 ────────────────────────────────────────

@pytest.mark.asyncio
async def test_scaffold_invalid_name_starts_with_digit(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "1BadName", "agent_type": "service"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


# ── TC-10-07: 이름 유효성 — 공백 포함 ───────────────────────────────────────

@pytest.mark.asyncio
async def test_scaffold_invalid_name_with_space(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "Bad Name", "agent_type": "service"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


# ── TC-10-08: 무효 agent_type ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_scaffold_invalid_agent_type(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "ValidName", "agent_type": "nonexistent"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


# ── TC-10-09: ZIP 내 meta.json 포함 ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_scaffold_zip_contains_meta_json(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "MyAgent", "agent_type": "service"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    files = _zip_files(resp.content)
    assert "MyAgent-meta.json" in files


# ── TC-10-10: meta.json 내 agent_type 일치 ───────────────────────────────────

@pytest.mark.asyncio
async def test_scaffold_meta_json_agent_type_matches(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "TypeAgent", "agent_type": "rag"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    meta_str = _zip_read(resp.content, "TypeAgent-meta.json")
    meta = json.loads(meta_str)
    assert meta["agent_type"] == "rag"


# ── TC-10-11: meta.json description/domain 반영 ──────────────────────────────

@pytest.mark.asyncio
async def test_scaffold_meta_json_description_domain(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={
            "agent_name": "DescAgent",
            "agent_type": "service",
            "description": "테스트 설명",
            "domain": "service.custom",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    meta_str = _zip_read(resp.content, "DescAgent-meta.json")
    meta = json.loads(meta_str)
    assert "테스트 설명" in meta.get("description", "")
    caps = meta.get("capabilities", [])
    assert any(c.get("domain") == "service.custom" for c in caps)


# ── TC-10-12: TypeScript 빌드 오류 없음 ──────────────────────────────────────

def test_typescript_build_no_errors():
    result = subprocess.run(
        ["pnpm", "tsc", "--noEmit"],
        cwd="front",
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"TS errors:\n{result.stdout}\n{result.stderr}"
