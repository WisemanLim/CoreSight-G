"""사용자 관리 라우터 (F5 RBAC).

참조: SmartHaccp-MultiAgent app/routers/router_users.py
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.deps import require_role
from app.db import execute_write, fetch_all, fetch_one, _PH

router = APIRouter(prefix="/api/users", tags=["users"])


class UserCreate(BaseModel):
    user_id: str
    username: str
    password: str
    role: str = "user"
    email: str = ""


@router.get("/")
async def list_users(user: dict = Depends(require_role("supervisor", "admin"))):
    rows = await fetch_all(
        "SELECT serial, user_id, username, email, role, status, created_at FROM tbl_users ORDER BY serial"
    )
    return {"users": rows, "total": len(rows)}


@router.post("/", status_code=201)
async def create_user(
    body: UserCreate,
    user: dict = Depends(require_role("supervisor", "admin")),
):
    from app.core.security import hash_password
    existing = await fetch_one(
        f"SELECT user_id FROM tbl_users WHERE user_id = {_PH}", (body.user_id,)
    )
    if existing:
        raise HTTPException(status_code=409, detail="이미 존재하는 사용자 ID입니다")
    await execute_write(
        f"INSERT INTO tbl_users (user_id, username, email, password, role) VALUES ({_PH},{_PH},{_PH},{_PH},{_PH})",
        (body.user_id, body.username, body.email, hash_password(body.password), body.role),
    )
    return {"message": "사용자 생성 완료", "user_id": body.user_id}


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current: dict = Depends(require_role("supervisor")),
):
    if user_id == current.get("sub"):
        raise HTTPException(status_code=400, detail="본인 계정은 삭제할 수 없습니다")
    row = await fetch_one(f"SELECT user_id FROM tbl_users WHERE user_id = {_PH}", (user_id,))
    if not row:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    await execute_write(f"DELETE FROM tbl_users WHERE user_id = {_PH}", (user_id,))
    return {"message": "삭제 완료"}
