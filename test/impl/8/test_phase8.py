"""Phase 9 — F22 Agent 카탈로그 시스템 통합 시험 (Iteration 8).

TC-8-01~12: agent_type, catalog API, scaffold API, sql_path 저장 버그 수정 검증.
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

    uid, pw = "p8_admin", "Admin8!"
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
    resp = await client.post("/api/auth/login", json={"user_id": "p8_admin", "password": "Admin8!"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _make_zip(name: str, files: dict[str, str]) -> bytes:
    """dict {filename: content} → ZIP bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for fname, content in files.items():
            zf.writestr(fname, content)
    return buf.getvalue()


# ── TC-8-01: list addons — agent_type 필드 포함 ───────────────────────────────

@pytest.mark.asyncio
async def test_list_addons_has_agent_type(client, token):
    resp = await client.get("/api/addon-agents/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "addons" in data
    # 항목이 있으면 agent_type 필드 확인
    if data["addons"]:
        for addon in data["addons"]:
            assert "agent_type" in addon, f"agent_type 필드 없음: {addon}"


# ── TC-8-02: catalog 전체 반환 ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_catalog_returns_groups_and_items(client, token):
    resp = await client.get("/api/addon-agents/catalog", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "groups" in data
    assert "items" in data
    assert "total" in data
    assert isinstance(data["groups"], dict)
    assert isinstance(data["items"], list)


# ── TC-8-03: catalog type 필터 ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_catalog_filter_by_type(client, token):
    resp = await client.get(
        "/api/addon-agents/catalog?agent_type=app",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item.get("agent_type") == "app", f"유형 필터 실패: {item}"


# ── TC-8-04: templates/list — agent_type 필드 포함 ───────────────────────────

@pytest.mark.asyncio
async def test_template_list_has_agent_type(client, token):
    resp = await client.get("/api/addon-agents/templates/list", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    templates = resp.json().get("templates", [])
    assert len(templates) >= 1, "템플릿이 최소 1개 이상 있어야 함"
    for t in templates:
        assert "agent_type" in t, f"agent_type 없음: {t}"
        assert "description" in t, f"description 없음: {t}"


# ── TC-8-05: scaffold — Board(app) ZIP 반환 ──────────────────────────────────

@pytest.mark.asyncio
async def test_scaffold_returns_zip(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "TestBoard", "agent_type": "app", "description": "테스트 게시판"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "application/zip" in resp.headers.get("content-type", "")
    # ZIP 파싱 가능 여부
    buf = io.BytesIO(resp.content)
    with zipfile.ZipFile(buf) as zf:
        names = zf.namelist()
    assert len(names) > 0, "ZIP이 비어 있음"


# ── TC-8-06: scaffold — 잘못된 agent_name (숫자 시작) ─────────────────────────

@pytest.mark.asyncio
async def test_scaffold_invalid_name(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "1Invalid", "agent_type": "app"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


# ── TC-8-07: scaffold — 잘못된 agent_type ────────────────────────────────────

@pytest.mark.asyncio
async def test_scaffold_invalid_type(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "ValidName", "agent_type": "unknown-type"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


# ── TC-8-08: scaffold ZIP 내용 — meta.json + app.py 포함 ──────────────────────

@pytest.mark.asyncio
async def test_scaffold_zip_contains_meta_and_app(client, token):
    resp = await client.post(
        "/api/addon-agents/scaffold",
        json={"agent_name": "MyService", "agent_type": "service"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    buf = io.BytesIO(resp.content)
    with zipfile.ZipFile(buf) as zf:
        names = zf.namelist()
    assert any("meta.json" in n for n in names), f"meta.json 없음: {names}"
    assert any("app.py" in n for n in names), f"app.py 없음: {names}"


# ── TC-8-09: ZIP 업로드 — meta.json 포함 → agent_type 저장 ──────────────────

@pytest.mark.asyncio
async def test_upload_with_meta_json_sets_agent_type(client, token):
    meta = {
        "agent_type": "service",
        "version": "1.0.0",
        "description": "테스트 서비스",
        "capabilities": [],
    }
    zip_bytes = _make_zip("TestSvc", {
        "TestSvc-app.py": "from fastapi import APIRouter\nrouter = APIRouter()\n@router.get('/ping')\ndef ping(): return {'ok': True}\n",
        "TestSvc-meta.json": json.dumps(meta),
    })
    resp = await client.post(
        "/api/addon-agents/upload?force=true",
        files={"file": ("TestSvc.zip", zip_bytes, "application/zip")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("agent_type") == "service", f"agent_type 저장 실패: {data}"
    # 정리
    await client.delete("/api/addon-agents/testsvc", headers={"Authorization": f"Bearer {token}"})


# ── TC-8-10: meta.json 없는 ZIP 업로드 → agent_type=app 기본값 ────────────────

@pytest.mark.asyncio
async def test_upload_without_meta_defaults_to_app(client, token):
    zip_bytes = _make_zip("NoMetaAgent", {
        "NoMetaAgent-app.py": "from fastapi import APIRouter\nrouter = APIRouter()\n@router.get('/ping')\ndef ping(): return {'ok': True}\n",
    })
    resp = await client.post(
        "/api/addon-agents/upload?force=true",
        files={"file": ("NoMetaAgent.zip", zip_bytes, "application/zip")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("agent_type") == "app", f"기본값 app 아님: {data}"
    # 정리
    await client.delete("/api/addon-agents/nometaagent", headers={"Authorization": f"Bearer {token}"})


# ── TC-8-11: sql_path 저장 확인 (BUG-v1.4-01 수정 검증) ─────────────────────

@pytest.mark.asyncio
async def test_upload_sql_path_stored(client, token):
    from app.db import _PH, fetch_one

    zip_bytes = _make_zip("SqlAgent", {
        "SqlAgent-app.py": "from fastapi import APIRouter\nrouter = APIRouter()\n@router.get('/ping')\ndef ping(): return {'ok': True}\n",
        "SqlAgent-sql.sql": "CREATE TABLE IF NOT EXISTS tbl_sqlagent_test (id INTEGER PRIMARY KEY);",
    })
    resp = await client.post(
        "/api/addon-agents/upload?force=true",
        files={"file": ("SqlAgent.zip", zip_bytes, "application/zip")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    row = await fetch_one(
        f"SELECT sql_path FROM tbl_addon_agents WHERE agent_key = {_PH}", ("sqlagent",)
    )
    assert row is not None
    assert row.get("sql_path"), f"sql_path 비어있음 (BUG-v1.4-01 미수정): {row}"
    assert "sqlagent" in row["sql_path"].lower(), f"sql_path 경로 이상: {row['sql_path']}"

    # 정리
    await client.delete("/api/addon-agents/sqlagent", headers={"Authorization": f"Bearer {token}"})


# ── TC-8-12: catalog 무효 type filter — 빈 결과 (필터 무시) ──────────────────

@pytest.mark.asyncio
async def test_catalog_invalid_type_filter_returns_all(client, token):
    resp_all = await client.get(
        "/api/addon-agents/catalog",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp_invalid = await client.get(
        "/api/addon-agents/catalog?agent_type=invalid-type",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_all.status_code == 200
    assert resp_invalid.status_code == 200
    # 무효 type은 필터 무시 → 전체와 동일 total
    total_all = resp_all.json()["total"]
    total_invalid = resp_invalid.json()["total"]
    assert total_all == total_invalid, f"무효 필터가 적용됨: all={total_all}, invalid={total_invalid}"
