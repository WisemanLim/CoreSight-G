"""Skeleton — Addon Agent 최소 골격. [CUSTOMIZE] 도메인 로직으로 교체하세요.

마운트 경로: /api/addon/skeleton/...
엔드포인트:
  GET  /items       항목 목록
  POST /items       항목 생성
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.db import _PH, execute_insert, fetch_all

router = APIRouter(tags=["skeleton-agent"])


class ItemIn(BaseModel):
    name: str
    note: str = ""


@router.get("/items")
async def list_items(user: dict = Depends(get_current_user)):
    rows = await fetch_all("SELECT id, name, note, created_at FROM tbl_skeleton_items ORDER BY id DESC")
    return {"items": rows}


@router.post("/items", status_code=201)
async def create_item(body: ItemIn, user: dict = Depends(get_current_user)):
    item_id = await execute_insert(
        f"INSERT INTO tbl_skeleton_items (name, note, created_by) VALUES ({_PH}, {_PH}, {_PH})",
        (body.name, body.note, user["user_id"]),
    )
    return {"id": item_id, "name": body.name}
