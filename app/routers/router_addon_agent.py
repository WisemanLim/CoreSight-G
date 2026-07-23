"""Addon Agent 관리 라우터 — ZIP 업로드 핫 디플로이 (F4) + Agent 카탈로그 (F22)."""
import io
import json
import re
import shutil
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from app.addon_agent_loader import load_router
from app.core.deps import get_current_user, require_role
from app.db import execute_write, fetch_all, fetch_one, _PH

router = APIRouter(prefix="/api/addon-agents", tags=["addon-agents"])

_DEPLOYED = Path("addon-agents/deployed")
_TEMPLATES = Path("addon-agents/_templates")
_FRONT_DEPLOYED = Path("front/src/pages/addon/deployed")
_MAX_SIZE = 10 * 1024 * 1024  # 10 MB

_VALID_TYPES = {
    "app", "service", "tool-proxy", "rag", "reviewer", "execution", "hitl", "memory", "federation",
    "monitoring",  # 관제 Addon (PRD §7 Addon-first) — tbl_agent_config 미등록, is_active 로만 관리
}

# type → template directory name mapping
_TYPE_TEMPLATE = {
    "app": "Board",
    "service": "ServiceAgent",
    "tool-proxy": "ToolProxyAgent",
    "rag": "RagAgent",
    "reviewer": "ServiceAgent",
    "execution": "ServiceAgent",
    "hitl": "ServiceAgent",
    "memory": "ServiceAgent",
    "federation": "ServiceAgent",
}


def _pg_to_sqlite(sql: str) -> str:
    """PostgreSQL DDL → SQLite 호환 변환 (local SQLite 환경에서만 적용)."""
    from app.core.config import settings
    if not settings.database_url.startswith("sqlite"):
        return sql
    sql = re.sub(r"\bSERIAL\b", "INTEGER", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\bBOOLEAN\b", "INTEGER", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\bDEFAULT\s+NOW\s*\(\)", "DEFAULT CURRENT_TIMESTAMP", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\bDEFAULT\s+FALSE\b", "DEFAULT 0", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\bDEFAULT\s+TRUE\b", "DEFAULT 1", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\bVARCHAR\s*\(\s*\d+\s*\)", "TEXT", sql, flags=re.IGNORECASE)
    return sql


def _safe_extract(zf: zipfile.ZipFile, dest: Path) -> None:
    """경로 탐색 공격 방지: '..' 또는 절대 경로 포함 항목 차단."""
    for member in zf.namelist():
        if ".." in member or member.startswith("/"):
            raise ValueError(f"Unsafe path in ZIP: {member}")
    zf.extractall(dest)


def _parse_meta_json(dest: Path, zip_stem: str) -> dict:
    """ZIP 내 {AgentName}-meta.json 파싱. 없으면 기본값(type=app) 반환."""
    meta_file = dest / f"{zip_stem}-meta.json"
    if not meta_file.exists():
        return {"agent_type": "app", "capabilities": []}
    try:
        data = json.loads(meta_file.read_text(encoding="utf-8"))
        if data.get("agent_type") not in _VALID_TYPES:
            data["agent_type"] = "app"
        return data
    except Exception:
        return {"agent_type": "app", "capabilities": []}


@router.get("/templates/list")
async def list_templates(user: dict = Depends(get_current_user)):
    if not _TEMPLATES.exists():
        return {"templates": []}
    templates = []
    for d in sorted(_TEMPLATES.iterdir()):
        if not d.is_dir():
            continue
        # meta.json이 있으면 유형 정보 읽기
        meta_files = list(d.glob("*-meta.json"))
        agent_type = "app"
        description = ""
        if meta_files:
            try:
                meta = json.loads(meta_files[0].read_text(encoding="utf-8"))
                agent_type = meta.get("agent_type", "app")
                description = meta.get("description", "")
            except Exception:
                pass
        templates.append({
            "name": d.name,
            "filename": f"{d.name}.zip",
            "agent_type": agent_type,
            "description": description,
            "has_zip": (_TEMPLATES / f"{d.name}.zip").exists(),
        })
    return {"templates": templates}


@router.get("/catalog")
async def list_catalog(
    agent_type: str | None = None,
    user: dict = Depends(get_current_user),
):
    """등록된 Addon Agent 목록을 유형별로 그룹핑하여 반환."""
    sql = (
        "SELECT agent_key, agent_name, api_prefix, agent_type, has_app, has_front, "
        "is_builtin, is_active, uploaded_by, uploaded_at FROM tbl_addon_agents "
    )
    params: tuple = ()
    if agent_type and agent_type in _VALID_TYPES:
        sql += f"WHERE agent_type = {_PH} "
        params = (agent_type,)
    sql += "ORDER BY is_builtin DESC, uploaded_at DESC"
    rows = await fetch_all(sql, params)

    # 유형별 그룹핑
    groups: dict[str, list] = {}
    for row in rows:
        t = row.get("agent_type") or "app"
        groups.setdefault(t, []).append(row)

    return {
        "total": len(rows),
        "groups": groups,
        "items": rows,
    }


@router.get("/templates/download/{name}")
async def download_template(name: str, user: dict = Depends(get_current_user)):
    if ".." in name or "/" in name or "\\" in name:
        raise HTTPException(status_code=400, detail="Invalid template name")
    zip_path = _TEMPLATES / f"{name}.zip"
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Template zip not found")
    return FileResponse(str(zip_path), media_type="application/zip", filename=f"{name}.zip")


@router.get("/guide")
async def get_guide(user: dict = Depends(get_current_user)):
    """addon-agents/README.md 내용 반환."""
    readme = Path("addon-agents/README.md")
    if not readme.exists():
        return {"content": ""}
    return {"content": readme.read_text(encoding="utf-8")}


@router.get("/")
async def list_addons(user: dict = Depends(get_current_user)):
    rows = await fetch_all(
        "SELECT agent_key, agent_name, api_prefix, agent_type, has_app, has_front, "
        "is_builtin, is_active, uploaded_by, uploaded_at "
        "FROM tbl_addon_agents ORDER BY is_builtin DESC, uploaded_at DESC"
    )
    return {"addons": rows}


class ScaffoldRequest(BaseModel):
    agent_name: str
    agent_type: str = "app"
    description: str = ""
    domain: str = ""


@router.post("/scaffold")
async def scaffold_addon(
    body: ScaffoldRequest,
    user: dict = Depends(get_current_user),
):
    """agent_type + name으로 스캐폴딩 ZIP 생성·다운로드."""
    # 이름 검증: PascalCase 또는 단어 허용
    name = body.agent_name.strip()
    if not name or not re.match(r"^[A-Za-z][A-Za-z0-9_-]*$", name):
        raise HTTPException(status_code=400, detail="agent_name은 영문자로 시작해야 합니다 (PascalCase 권장)")
    if body.agent_type not in _VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"agent_type은 {sorted(_VALID_TYPES)} 중 하나여야 합니다")

    # 기반 템플릿 디렉터리 결정
    tmpl_dir_name = _TYPE_TEMPLATE.get(body.agent_type, "ServiceAgent")
    tmpl_dir = _TEMPLATES / tmpl_dir_name
    if not tmpl_dir.exists():
        raise HTTPException(status_code=404, detail=f"템플릿 미존재: {tmpl_dir_name}")

    # ZIP을 메모리에서 생성 (템플릿 파일 복사 + 이름 치환)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for src_file in sorted(tmpl_dir.iterdir()):
            if src_file.is_dir() or src_file.suffix in (".pyc",):
                continue
            # 파일명: 템플릿명 → 요청 이름으로 치환
            new_filename = src_file.name.replace(tmpl_dir_name, name)
            try:
                content = src_file.read_text(encoding="utf-8")
                # 파일 내 템플릿명도 치환 (클래스명, 변수명 등)
                content = content.replace(tmpl_dir_name, name)
                # meta.json의 description/domain 업데이트
                if new_filename.endswith("-meta.json"):
                    try:
                        meta = json.loads(content)
                        if body.description:
                            meta["description"] = body.description
                        if body.domain:
                            for cap in meta.get("capabilities", []):
                                cap["domain"] = body.domain
                        meta["agent_type"] = body.agent_type
                        content = json.dumps(meta, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                zf.writestr(new_filename, content)
            except UnicodeDecodeError:
                # 바이너리 파일은 그대로 복사
                zf.write(src_file, new_filename)

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{name}.zip"'},
    )


@router.patch("/{agent_key}/toggle")
async def toggle_addon(
    agent_key: str,
    user: dict = Depends(require_role("supervisor", "admin")),
):
    """Addon is_active 토글 — tbl_agent_config.is_enabled 도 동기화."""
    row = await fetch_one(
        f"SELECT is_active, router_path, api_prefix, sql_path FROM tbl_addon_agents WHERE agent_key = {_PH}", (agent_key,)
    )
    if not row:
        raise HTTPException(status_code=404, detail="Addon not found")
    new_active = 0 if row["is_active"] else 1
    await execute_write(
        f"UPDATE tbl_addon_agents SET is_active = {_PH} WHERE agent_key = {_PH}",
        (new_active, agent_key),
    )
    await execute_write(
        f"UPDATE tbl_agent_config SET is_enabled = {_PH} WHERE agent_key = {_PH}",
        (new_active, agent_key),
    )
    from app import addon_agent_loader
    if new_active and row.get("router_path"):
        if row.get("sql_path"):
            await addon_agent_loader.apply_sql(row["sql_path"])
        addon_agent_loader.load_router(agent_key, row["router_path"], row["api_prefix"])
    elif not new_active and row.get("api_prefix"):
        addon_agent_loader.unload_router(agent_key, row["api_prefix"])
        from app.services import mcp_proxy_server
        await mcp_proxy_server.stop(agent_key)
        await execute_write(
            f"DELETE FROM tbl_mcp_configs WHERE agent_key = {_PH}", (agent_key,)
        )
    return {"agent_key": agent_key, "is_active": bool(new_active)}


@router.post("/upload")
async def upload_addon(
    file: UploadFile = File(...),
    force: bool = False,
    user: dict = Depends(require_role("supervisor", "admin")),
):
    """ZIP 업로드 → 유효성 검사 → 파일 배포 → SQL 실행 → 핫 라우터 등록 → DB 기록."""
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="ZIP 파일만 허용됩니다")

    raw = await file.read()
    if len(raw) > _MAX_SIZE:
        raise HTTPException(status_code=400, detail="ZIP 최대 크기 10MB 초과")

    zip_stem = Path(file.filename).stem       # e.g. "ExampleAddon"
    agent_key = zip_stem.lower()              # e.g. "exampleaddon"
    agent_name = zip_stem

    existing = await fetch_one(
        f"SELECT agent_key FROM tbl_addon_agents WHERE agent_key = {_PH}", (agent_key,)
    )
    if existing and not force:
        raise HTTPException(
            status_code=409,
            detail=f"'{agent_key}' already exists. Use force=true to overwrite.",
        )

    dest = _DEPLOYED / agent_key
    dest.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            _safe_extract(zf, dest)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="유효하지 않은 ZIP 파일")

    app_file = dest / f"{zip_stem}-app.py"
    front_file = dest / f"{zip_stem}-front.tsx"
    has_app = app_file.exists()
    has_front = front_file.exists()

    if not has_app and not has_front:
        raise HTTPException(
            status_code=400,
            detail=f"{zip_stem}-app.py 또는 {zip_stem}-front.tsx 중 하나가 ZIP에 있어야 합니다",
        )

    # Front TSX → front/src/pages/addon/deployed/{agent_key}.tsx
    if has_front:
        _FRONT_DEPLOYED.mkdir(parents=True, exist_ok=True)
        shutil.copy2(front_file, _FRONT_DEPLOYED / f"{agent_key}.tsx")

    # SQL 실행 (있으면)
    sql_file = dest / f"{zip_stem}-sql.sql"
    sql_path_val = str(sql_file) if sql_file.exists() else ""
    if sql_file.exists():
        sql_text = sql_file.read_text(encoding="utf-8")
        for stmt in sql_text.split(";"):
            stmt = _pg_to_sqlite(stmt.strip())
            if stmt:
                try:
                    await execute_write(stmt)
                except Exception:
                    pass  # IF NOT EXISTS 등 기존 객체 충돌 무시

    # meta.json 파싱 (F22)
    meta = _parse_meta_json(dest, zip_stem)
    agent_type = meta.get("agent_type", "app")
    meta_json_val = json.dumps(meta, ensure_ascii=False)

    # 라우터 핫 로드 (app.py 있을 때만)
    api_prefix = f"/api/addon/{agent_key}"
    ok = False
    if has_app:
        ok = load_router(agent_key, str(app_file), api_prefix)
        if not ok:
            raise HTTPException(status_code=500, detail="라우터 로드 실패 — app.py 문법 오류 확인")

    # DB 등록
    router_path = str(app_file) if has_app else ""
    if existing:
        await execute_write(
            f"UPDATE tbl_addon_agents SET agent_name={_PH}, router_path={_PH}, "
            f"api_prefix={_PH}, has_app={_PH}, has_front={_PH}, sql_path={_PH}, "
            f"agent_type={_PH}, meta_json={_PH}, "
            f"uploaded_by={_PH}, uploaded_at=CURRENT_TIMESTAMP "
            f"WHERE agent_key={_PH}",
            (agent_name, router_path, api_prefix, int(has_app), int(has_front),
             sql_path_val, agent_type, meta_json_val, user["sub"], agent_key),
        )
    else:
        await execute_write(
            f"INSERT INTO tbl_addon_agents "
            f"(agent_key, agent_name, router_path, api_prefix, has_app, has_front, "
            f"sql_path, agent_type, meta_json, uploaded_by) "
            f"VALUES ({_PH},{_PH},{_PH},{_PH},{_PH},{_PH},{_PH},{_PH},{_PH},{_PH})",
            (agent_key, agent_name, router_path, api_prefix, int(has_app), int(has_front),
             sql_path_val, agent_type, meta_json_val, user["sub"]),
        )

    # Agent 설정 등록 — monitoring 타입(관제 Addon, PRD §7 Addon-first)은 tbl_agent_config 를
    # 쓰지 않고 tbl_addon_agents.is_active 로만 관리한다(에이전트 관리 "ADDON 에이전트" 섹션 전용).
    # 그 외 addon_type(app/tool-proxy/rag 등, 채팅 라우팅용)은 기존대로 관제 Agent 토글 등록.
    if agent_type != "monitoring":
        await execute_write(
            f"INSERT INTO tbl_agent_config (agent_key, agent_name, is_enabled) "
            f"VALUES ({_PH},{_PH},1) ON CONFLICT(agent_key) DO NOTHING",
            (agent_key, agent_name),
        )

    # Capability 인덱스 등록 (F23) — meta_json의 capabilities 배열 저장
    capabilities = meta.get("capabilities", [])
    if capabilities:
        # 기존 capability 제거 후 재삽입 (force=true 대응)
        try:
            await execute_write(
                f"DELETE FROM tbl_addon_agent_capabilities WHERE agent_key = {_PH}", (agent_key,)
            )
        except Exception:
            pass
        for cap in capabilities:
            verb = cap.get("verb", "")
            domain = cap.get("domain", "")
            if not verb or not domain:
                continue
            cap_key = f"{agent_key}.{verb}.{domain}"
            try:
                await execute_write(
                    f"INSERT OR IGNORE INTO tbl_addon_agent_capabilities "
                    f"(agent_key, capability_key, verb, domain, description, input_schema, output_schema, qos_json) "
                    f"VALUES ({_PH},{_PH},{_PH},{_PH},{_PH},{_PH},{_PH},{_PH})",
                    (
                        agent_key, cap_key, verb, domain,
                        cap.get("description", ""),
                        json.dumps(cap.get("input_schema")) if cap.get("input_schema") else None,
                        json.dumps(cap.get("output_schema")) if cap.get("output_schema") else None,
                        json.dumps(cap.get("qos")) if cap.get("qos") else None,
                    ),
                )
            except Exception:
                pass

    return {
        "agent_key": agent_key,
        "agent_name": agent_name,
        "agent_type": agent_type,
        "api_prefix": api_prefix,
        "has_app": has_app,
        "has_front": has_front,
        "message": "배포 완료" + (" (프론트 포함 — 재빌드 필요)" if has_front else ""),
    }


def _extract_table_names(sql_path: str) -> list[str]:
    """SQL 파일에서 CREATE TABLE 대상 테이블명 추출."""
    try:
        src = Path(sql_path).read_text(encoding="utf-8")
        return re.findall(r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)", src, re.IGNORECASE)
    except Exception:
        return []


class AddonPatch(BaseModel):
    agent_name: str | None = None


@router.patch("/{agent_key}")
async def patch_addon(
    agent_key: str,
    body: AddonPatch,
    user: dict = Depends(require_role("supervisor", "admin")),
):
    """Addon agent 속성 수정 (이름 등)."""
    row = await fetch_one(
        f"SELECT agent_key FROM tbl_addon_agents WHERE agent_key = {_PH}", (agent_key,)
    )
    if not row:
        raise HTTPException(status_code=404, detail="Addon not found")
    if body.agent_name:
        await execute_write(
            f"UPDATE tbl_addon_agents SET agent_name = {_PH} WHERE agent_key = {_PH}",
            (body.agent_name, agent_key),
        )
        await execute_write(
            f"UPDATE tbl_agent_config SET agent_name = {_PH} WHERE agent_key = {_PH}",
            (body.agent_name, agent_key),
        )
    return {"message": "Updated", "agent_key": agent_key}


@router.delete("/{agent_key}")
async def delete_addon(
    agent_key: str,
    user: dict = Depends(require_role("supervisor", "admin")),
):
    row = await fetch_one(
        f"SELECT agent_key, sql_path, is_builtin FROM tbl_addon_agents WHERE agent_key = {_PH}",
        (agent_key,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Addon not found")
    if row.get("is_builtin"):
        raise HTTPException(status_code=403, detail="내장 에이전트는 삭제할 수 없습니다.")

    # 1. addon이 생성한 테이블 DROP
    sql_path = row.get("sql_path") or ""
    if sql_path:
        for table in _extract_table_names(sql_path):
            try:
                await execute_write(f"DROP TABLE IF EXISTS {table}")
            except Exception:
                pass

    # 2. 배포 파일 제거
    agent_dir = _DEPLOYED / agent_key
    if agent_dir.exists():
        shutil.rmtree(agent_dir)

    front_tsx = _FRONT_DEPLOYED / f"{agent_key}.tsx"
    if front_tsx.exists():
        front_tsx.unlink()

    # 3. MCP 프록시 종료 + 설정 삭제
    from app.services import mcp_proxy_server
    await mcp_proxy_server.stop(agent_key)
    await execute_write(
        f"DELETE FROM tbl_mcp_configs WHERE agent_key = {_PH}", (agent_key,)
    )

    # 4. DB 레코드 삭제
    await execute_write(
        f"DELETE FROM tbl_addon_agents WHERE agent_key = {_PH}", (agent_key,)
    )
    await execute_write(
        f"DELETE FROM tbl_agent_config WHERE agent_key = {_PH}", (agent_key,)
    )
    return {"message": f"'{agent_key}' 삭제 완료. 라우터 제거는 앱 재시작 필요."}
