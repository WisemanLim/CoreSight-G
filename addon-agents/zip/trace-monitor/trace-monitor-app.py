"""trace-monitor — 수집 파이프라인 트레이스(OTel/Jaeger) 조회 Addon Agent (PRD P1).

마운트 경로: /api/addon/trace-monitor/...
엔드포인트:
  GET  /tools              지원 도구 목록
  POST /tools/{tool_name}  도구 실행
  GET  /status             계측 서비스 수 요약

Domain Agent 연동 규약: `router` + `_TOOLS` + `TOOL_EXECUTORS` + `SYSTEM_PROMPT` export.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.services import jaeger
from app.services.jaeger import JaegerError

router = APIRouter(tags=["trace-monitor"])

SYSTEM_PROMPT = (
    "당신은 CoreSight-G 플랫폼의 트레이스 분석 전문가입니다. "
    "제공된 도구로 Jaeger 에서 실제 분산 트레이스(OTel)를 조회한 뒤 답변합니다. "
    "조회 없이 지연·오류를 추정하지 마세요. "
    "해석 기준: duration 급증 = 수집 파이프라인 병목(Prometheus/Loki 응답 지연 확인), "
    "errors>0 스팬 = 하위 호출 실패, span_count 급증 = 비정상 재시도. "
    "대상은 플랫폼 자체 파이프라인(coresight-g-api)이며, 앱 계층 확장 시 서비스가 추가됩니다."
)

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "list_services",
        "description": "트레이스가 수집되는(계측된) 서비스 목록을 조회합니다.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "search_traces",
        "description": "서비스의 최근 트레이스 요약(지연·스팬 수·오류 수)을 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {"type": "string", "description": "서비스명 (기본 coresight-g-api)"},
                "minutes": {"type": "integer", "description": "조회 범위(분), 기본 30"},
                "limit": {"type": "integer", "description": "최대 건수, 기본 20"},
                "min_duration_ms": {"type": "integer", "description": "이 지연(ms) 이상만 조회 (병목 탐지)"},
            },
        },
    },
]


async def _list_services(tool_input: dict) -> dict:
    try:
        return {"services": await jaeger.services()}
    except JaegerError as exc:
        return {"error": str(exc)}


async def _search_traces(tool_input: dict) -> dict:
    try:
        traces = await jaeger.search_traces(
            service=tool_input.get("service") or "coresight-g-api",
            minutes=int(tool_input.get("minutes") or 30),
            limit=int(tool_input.get("limit") or 20),
            min_duration_ms=tool_input.get("min_duration_ms"),
        )
        return {"count": len(traces), "traces": traces}
    except JaegerError as exc:
        return {"error": str(exc)}


TOOL_EXECUTORS: dict[str, Any] = {
    "list_services": _list_services,
    "search_traces": _search_traces,
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
        svcs = await jaeger.services()
    except JaegerError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"instrumented_services": len(svcs), "services": svcs}
