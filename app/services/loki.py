"""Loki HTTP API 클라이언트 — 로그 검색 공통 서비스 (PRD P1).

query_range(LogQL) 와 라벨 조회만 사용. 수집(push)은 mock 생성기/Promtail 담당.
"""
import logging
import time
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

_TIMEOUT = 5.0


class LokiError(RuntimeError):
    """Loki 응답 실패 (연결 불가·쿼리 오류)."""


async def _get(path: str, params: dict) -> dict:
    url = f"{settings.loki_url}{path}"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, params=params)
        data = resp.json()
    except Exception as exc:
        raise LokiError(f"Loki 연결 실패: {exc}") from exc
    if data.get("status") != "success":
        raise LokiError(f"쿼리 실패: {data.get('error', resp.text[:200])}")
    return data


async def search(
    logql: str, minutes: int = 30, limit: int = 100
) -> list[dict[str, Any]]:
    """LogQL range query → [{ts, line, labels}] 평탄화(최신순)."""
    end = time.time_ns()
    start = end - minutes * 60 * 1_000_000_000
    data = await _get(
        "/loki/api/v1/query_range",
        {"query": logql, "start": start, "end": end, "limit": limit, "direction": "backward"},
    )
    entries: list[dict[str, Any]] = []
    for stream in data["data"]["result"]:
        labels = stream.get("stream", {})
        for ts, line in stream.get("values", []):
            entries.append({"ts": int(ts), "line": line, "labels": labels})
    entries.sort(key=lambda e: e["ts"], reverse=True)
    return entries[:limit]


async def labels(name: str = "job") -> list[str]:
    """라벨 값 목록 (기본 job — syslog/dmesg/bmc)."""
    data = await _get(f"/loki/api/v1/label/{name}/values", {})
    return data.get("data", [])


def build_logql(job: str | None = None, keyword: str | None = None, level: str | None = None) -> str:
    """간단 파라미터 → LogQL 조립 (비 LogQL 사용자용)."""
    selectors = []
    if job:
        selectors.append(f'job="{job}"')
    if level:
        selectors.append(f'level="{level}"')
    selector = "{" + (", ".join(selectors) if selectors else 'job=~".+"') + "}"
    if keyword:
        escaped = keyword.replace("\\", "\\\\").replace('"', '\\"')
        return f'{selector} |~ "(?i){escaped}"'
    return selector
