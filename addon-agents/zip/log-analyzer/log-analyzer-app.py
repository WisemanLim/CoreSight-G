"""log-analyzer — 시스템/dmesg/BMC 로그 검색·이상 패턴 분석 Addon Agent (PRD P1).

마운트 경로: /api/addon/log-analyzer/...
엔드포인트:
  GET  /tools              지원 도구 목록
  POST /tools/{tool_name}  도구 실행
  GET  /status             최근 1시간 error 로그 요약

Domain Agent 연동 규약: `router` + `_TOOLS` + `TOOL_EXECUTORS` + `SYSTEM_PROMPT` export.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.services import loki
from app.services.loki import LokiError

router = APIRouter(tags=["log-analyzer"])

SYSTEM_PROMPT = (
    "당신은 CoreSight-G 플랫폼의 로그 분석 전문가입니다. "
    "제공된 도구로 Loki 에서 실제 시스템(syslog)/커널(dmesg)/BMC 로그를 조회한 뒤 답변합니다. "
    "조회 없이 로그 내용을 추정하지 마세요. "
    "이상 패턴 해석 기준: 'Xid' = GPU 장애 신호(즉시 조사), 'DEGRADED' = RAID 저하, "
    "'ECC' = 메모리 오류, 'AER' = PCIe 오류(반복 시 조사), 파일시스템 error = 디스크 점검. "
    "분석 결과는 원문 로그 라인 근거와 함께 제시합니다."
)

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_logs",
        "description": "로그를 검색합니다. job(syslog/dmesg/bmc), keyword, level(info/warning/error), minutes 지정 가능.",
        "input_schema": {
            "type": "object",
            "properties": {
                "job": {"type": "string", "enum": ["syslog", "dmesg", "bmc"]},
                "keyword": {"type": "string", "description": "포함 키워드 (대소문자 무시)"},
                "level": {"type": "string", "enum": ["info", "warning", "error"]},
                "minutes": {"type": "integer", "description": "조회 범위(분), 기본 30"},
                "limit": {"type": "integer", "description": "최대 건수, 기본 50"},
            },
        },
    },
    {
        "name": "recent_errors",
        "description": "최근 error 레벨 로그를 전 소스에서 조회합니다 (기본 60분).",
        "input_schema": {
            "type": "object",
            "properties": {
                "minutes": {"type": "integer", "description": "조회 범위(분), 기본 60"},
            },
        },
    },
]


async def _search_logs(tool_input: dict) -> dict:
    logql = loki.build_logql(
        job=tool_input.get("job"),
        keyword=tool_input.get("keyword"),
        level=tool_input.get("level"),
    )
    try:
        entries = await loki.search(
            logql,
            minutes=int(tool_input.get("minutes") or 30),
            limit=int(tool_input.get("limit") or 50),
        )
        return {"query": logql, "count": len(entries), "entries": entries}
    except LokiError as exc:
        return {"error": str(exc)}


async def _recent_errors(tool_input: dict) -> dict:
    logql = loki.build_logql(level="error")
    try:
        entries = await loki.search(logql, minutes=int(tool_input.get("minutes") or 60), limit=50)
        return {"count": len(entries), "entries": entries}
    except LokiError as exc:
        return {"error": str(exc)}


TOOL_EXECUTORS: dict[str, Any] = {
    "search_logs": _search_logs,
    "recent_errors": _recent_errors,
}


# ─── REST 노출 (MCP/외부 연동·수동 점검용) ───────────────────────────────────

@router.get("/tools")
async def list_tools(user: dict = Depends(get_current_user)):
    return {"tools": _TOOLS}


@router.post("/tools/{tool_name}")
async def call_tool(tool_name: str, arguments: dict | None = None, user: dict = Depends(get_current_user)):
    executor = TOOL_EXECUTORS.get(tool_name)
    if executor is None:
        raise HTTPException(status_code=404, detail=f"알 수 없는 도구: {tool_name}")
    return {"result": await executor(arguments or {})}


@router.get("/status")
async def status(user: dict = Depends(get_current_user)):
    try:
        entries = await loki.search(loki.build_logql(level="error"), minutes=60, limit=50)
    except LokiError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"error_count_1h": len(entries)}
