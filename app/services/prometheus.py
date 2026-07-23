"""Prometheus HTTP API 클라이언트 — GPU/HW 메트릭·알람 조회 공통 서비스.

instant query(/api/v1/query), 활성 알람(/api/v1/alerts)만 사용한다.
range query 는 대시보드(P0 후속 차수)에서 추가 예정.
"""
import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

_TIMEOUT = 5.0


class PrometheusError(RuntimeError):
    """Prometheus 응답 실패 (연결 불가·쿼리 오류)."""


async def query(promql: str) -> list[dict[str, Any]]:
    """instant query 실행 → result 리스트([{metric, value}, ...]) 반환."""
    url = f"{settings.prometheus_url}/api/v1/query"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, params={"query": promql})
        data = resp.json()
    except Exception as exc:
        raise PrometheusError(f"Prometheus 연결 실패: {exc}") from exc
    if data.get("status") != "success":
        raise PrometheusError(f"쿼리 실패: {data.get('error', 'unknown')}")
    return data["data"]["result"]


async def query_range(promql: str, minutes: int, step_seconds: int) -> list[dict[str, Any]]:
    """range query 실행 → result 리스트([{metric, values: [[ts, v], ...]}, ...]) 반환."""
    import time

    end = time.time()
    params = {
        "query": promql,
        "start": end - minutes * 60,
        "end": end,
        "step": step_seconds,
    }
    url = f"{settings.prometheus_url}/api/v1/query_range"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, params=params)
        data = resp.json()
    except Exception as exc:
        raise PrometheusError(f"Prometheus 연결 실패: {exc}") from exc
    if data.get("status") != "success":
        raise PrometheusError(f"range 쿼리 실패: {data.get('error', 'unknown')}")
    return data["data"]["result"]


async def gpu_util_history(minutes: int = 30, step_seconds: int = 60) -> list[dict[str, Any]]:
    """GPU 별 utilization 시계열 (대시보드 스파크라인용)."""
    series = await query_range("DCGM_FI_DEV_GPU_UTIL", minutes, step_seconds)
    return [
        {
            "hostname": s["metric"].get("Hostname", "unknown"),
            "gpu": s["metric"].get("gpu", "?"),
            "points": [[float(ts), float(v)] for ts, v in s["values"]],
        }
        for s in sorted(series, key=lambda s: (s["metric"].get("Hostname", ""), s["metric"].get("gpu", "")))
    ]


async def active_alerts() -> list[dict[str, Any]]:
    """현재 활성(firing/pending) 알람 목록."""
    url = f"{settings.prometheus_url}/api/v1/alerts"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url)
        data = resp.json()
    except Exception as exc:
        raise PrometheusError(f"Prometheus 연결 실패: {exc}") from exc
    if data.get("status") != "success":
        raise PrometheusError(f"알람 조회 실패: {data.get('error', 'unknown')}")
    return data["data"]["alerts"]


def _scalar(sample: dict[str, Any]) -> float:
    return float(sample["value"][1])


async def gpu_snapshot() -> list[dict[str, Any]]:
    """GPU 별 핵심 지표 스냅샷 (PRD 1순위 메트릭)."""
    metric_names = {
        "util_percent": "DCGM_FI_DEV_GPU_UTIL",
        "vram_used_mib": "DCGM_FI_DEV_FB_USED",
        "vram_total_mib": "DCGM_FI_DEV_FB_TOTAL",
        "temperature_c": "DCGM_FI_DEV_GPU_TEMP",
        "power_watts": "DCGM_FI_DEV_POWER_USAGE",
        "xid_errors": "DCGM_FI_DEV_XID_ERRORS",
        "ecc_dbe_total": "DCGM_FI_DEV_ECC_DBE_VOL_TOTAL",
    }
    gpus: dict[tuple[str, str], dict[str, Any]] = {}
    for field, name in metric_names.items():
        for sample in await query(name):
            m = sample["metric"]
            key = (m.get("Hostname", "unknown"), m.get("gpu", "?"))
            entry = gpus.setdefault(key, {"hostname": key[0], "gpu": key[1]})
            entry[field] = _scalar(sample)
    result = sorted(gpus.values(), key=lambda g: (g["hostname"], g["gpu"]))
    for g in result:
        used, total = g.get("vram_used_mib"), g.get("vram_total_mib")
        if used is not None and total:
            g["vram_used_percent"] = round(used / total * 100, 1)
    return result


async def hardware_snapshot() -> list[dict[str, Any]]:
    """노드 별 서버 하드웨어 지표 스냅샷."""
    metric_names = {
        "cpu_usage_percent": "hw_cpu_usage_percent",
        "memory_total_bytes": "hw_memory_total_bytes",
        "memory_available_bytes": "hw_memory_available_bytes",
        "raid_degraded": "max by (Hostname) (hw_raid_degraded)",
        "psu_failed": "count by (Hostname) (hw_psu_status == 0)",
        "inlet_temp_celsius": "hw_inlet_temp_celsius",
    }
    nodes: dict[str, dict[str, Any]] = {}
    for field, promql in metric_names.items():
        for sample in await query(promql):
            host = sample["metric"].get("Hostname")
            if not host:  # Hostname 라벨 없는 집계 결과는 노드 스냅샷에서 제외
                continue
            entry = nodes.setdefault(host, {"hostname": host})
            entry[field] = _scalar(sample)
    for entry in nodes.values():  # PSU 장애 없으면 count 결과가 비므로 0 보정
        entry.setdefault("psu_failed", 0.0)
    return sorted(nodes.values(), key=lambda n: n["hostname"])
