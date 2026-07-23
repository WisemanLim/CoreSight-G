"""Jaeger HTTP API 클라이언트 — 트레이스 조회 공통 서비스 (PRD P1).

조회·분석은 trace-monitor addon 이 이 서비스를 사용한다 (Addon-first 원칙).
"""
import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

_TIMEOUT = 5.0


class JaegerError(RuntimeError):
    """Jaeger 응답 실패 (연결 불가·쿼리 오류)."""


async def _get(path: str, params: dict | None = None) -> dict:
    url = f"{settings.jaeger_url}{path}"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, params=params or {})
        data = resp.json()
    except Exception as exc:
        raise JaegerError(f"Jaeger 연결 실패: {exc}") from exc
    if resp.status_code != 200:
        raise JaegerError(f"조회 실패: HTTP {resp.status_code}")
    return data


async def services() -> list[str]:
    """계측된 서비스 목록."""
    data = await _get("/api/services")
    return [s for s in (data.get("data") or []) if s]


async def search_traces(
    service: str, minutes: int = 30, limit: int = 20, min_duration_ms: int | None = None
) -> list[dict[str, Any]]:
    """서비스 별 최근 트레이스 요약 목록 (최신순)."""
    params: dict[str, Any] = {"service": service, "lookback": f"{minutes}m", "limit": limit}
    if min_duration_ms:
        params["minDuration"] = f"{min_duration_ms}ms"
    data = await _get("/api/traces", params)
    traces = []
    for t in data.get("data") or []:
        spans = t.get("spans", [])
        root = min(spans, key=lambda s: s.get("startTime", 0)) if spans else {}
        traces.append(
            {
                "trace_id": t.get("traceID"),
                "root_operation": root.get("operationName"),
                "span_count": len(spans),
                "duration_ms": round(max((s.get("duration", 0) for s in spans), default=0) / 1000, 2),
                "start_time_us": root.get("startTime"),
                "errors": sum(
                    1 for s in spans for tag in s.get("tags", [])
                    if tag.get("key") == "error" and tag.get("value")
                ),
            }
        )
    traces.sort(key=lambda t: t.get("start_time_us") or 0, reverse=True)
    return traces
