"""Orchestrator Agent — 의도 분류 → 병렬 라우팅 → 결과 합성 (F1).

패턴: Classify(1~3 intents) → asyncio.gather() → Synthesize
model 파라미터: "ollama" → Ollama 직접 사용, None/Claude모델 → Anthropic 사용 후 Ollama fallback
"""
import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import anthropic
import httpx

from app.core.config import settings
from app.agents.addon_tool_agent import addon_agent_cls
from app.rules.keyword_matcher import format_response, match_rule_async
from app.services.llm_fallback import call_ollama

logger = logging.getLogger("uvicorn.error")

# 지원할 intent 카테고리 목록
_VALID_INTENTS: list[str] = [
    "gpu_monitoring",  # GPU 메트릭·알람 조회 (addon: gpu-monitor)
    "hardware",        # 서버 하드웨어 상태 조회 (addon: hw-monitor)
    "log_analysis",    # 로그 검색·이상 패턴 분석 (addon: log-analyzer)
    "trace_analysis",  # 트레이스 병목·오류 분석 (addon: trace-monitor)
    "storage",         # 스토리지(디스크/SMART/RAID) 진단 (addon: storage-monitor)
    "bmc",             # BMC/IPMI 센서·이벤트 (addon: bmc-monitor)
    "gpu_profiling",   # GPU 고급 프로파일링 (SM/Tensor/DRAM/throttle) (addon: gpu-profiler)
    "capacity_planning",  # 저활용 탐지·효율 리포트·카디널리티 (addon: capacity-planner)
    "anomaly_detection",  # z-score 이상 탐지·알람 상관분석 (addon: anomaly-detector)
    "network",         # NIC 오류/드롭/링크상태 (addon: net-monitor)
    "workload_correlation",  # 프로세스/잡별 GPU 점유 상관 (addon: workload-correlator)
    "general",         # 일반 질문 (Orchestrator 직접 응답)
]

# intent → Agent 클래스 매핑 — 구현체는 addon-agents/zip/<key>/ (PRD §7)
_AGENT_MAP: dict[str, Any] = {
    "gpu_monitoring": addon_agent_cls("gpu-monitor", "gpu_monitoring"),
    "hardware": addon_agent_cls("hw-monitor", "hardware"),
    "log_analysis": addon_agent_cls("log-analyzer", "log_analysis"),
    "trace_analysis": addon_agent_cls("trace-monitor", "trace_analysis"),
    "storage": addon_agent_cls("storage-monitor", "storage"),
    "bmc": addon_agent_cls("bmc-monitor", "bmc"),
    "gpu_profiling": addon_agent_cls("gpu-profiler", "gpu_profiling"),
    "capacity_planning": addon_agent_cls("capacity-planner", "capacity_planning"),
    "anomaly_detection": addon_agent_cls("anomaly-detector", "anomaly_detection"),
    "network": addon_agent_cls("net-monitor", "network"),
    "workload_correlation": addon_agent_cls("workload-correlator", "workload_correlation"),
}

# SSE 이벤트에 표시될 Agent 이름
_AGENT_LABELS: dict[str, str] = {
    "gpu_monitoring": "GPU 모니터링 Agent",
    "hardware":       "하드웨어 Agent",
    "log_analysis":   "로그 분석 Agent",
    "trace_analysis": "트레이스 분석 Agent",
    "storage":        "스토리지 진단 Agent",
    "bmc":            "BMC/IPMI Agent",
    "gpu_profiling":  "GPU 프로파일링 Agent",
    "capacity_planning": "용량 계획 Agent",
    "anomaly_detection": "이상 탐지 Agent",
    "network":        "네트워크 모니터링 Agent",
    "workload_correlation": "워크로드 상관 Agent",
    "general":        "일반 응답",
}

_TOOL_CALL_API: dict = {
    "name": "call_api",
    "description": (
        "Call a backend REST API to actually perform CRUD operations on addon agents. "
        "Use this tool whenever the user requests an action (create/read/update/delete data). "
        "NEVER fabricate data or pretend to perform operations — always call this tool first."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "method": {"type": "string", "enum": ["GET", "POST", "PATCH", "DELETE"]},
            "path": {"type": "string", "description": "Full API path, e.g. /api/addon/usermanager/users"},
            "body": {"type": "object", "description": "JSON request body (POST/PATCH)"},
            "params": {"type": "object", "description": "Query parameters (GET)"},
        },
        "required": ["method", "path"],
    },
}


async def _exec_api_call(
    method: str, path: str, body: dict | None, params: dict | None, token: str | None
) -> str:
    from app.main import app as _app  # lazy — no circular import at call time
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        transport = httpx.ASGITransport(app=_app)
        async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as c:
            fn = getattr(c, method.lower())
            kwargs: dict = {"headers": headers}
            if body is not None and method.upper() not in ("GET", "HEAD"):
                kwargs["json"] = body
            if params:
                kwargs["params"] = params
            resp = await fn(path, **kwargs)
            # Include status code so Claude knows if the call succeeded or failed
            return f"HTTP {resp.status_code}\n{resp.text}"
    except Exception as exc:
        return f"HTTP ERROR\n{json.dumps({'error': str(exc)})}"


def _parse_router_prefix(router_path: str) -> str:
    """AST-parse the router .py file and extract APIRouter(prefix=...) value."""
    import ast
    try:
        src = Path(router_path).read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            is_router_call = (
                (isinstance(fn, ast.Attribute) and fn.attr == "APIRouter")
                or (isinstance(fn, ast.Name) and fn.id == "APIRouter")
            )
            if not is_router_call:
                continue
            for kw in node.keywords:
                if kw.arg == "prefix" and isinstance(kw.value, ast.Constant):
                    return str(kw.value.value)
    except Exception:
        pass
    return ""


def _parse_create_model_fields(router_path: str) -> dict[str, list[str]]:
    """Extract XxxCreate/XxxUpdate(BaseModel) field names from router source."""
    import re
    result: dict[str, list[str]] = {}
    try:
        src = Path(router_path).read_text(encoding="utf-8")
        current: str | None = None
        for line in src.splitlines():
            m = re.match(r"^class (\w+)\(BaseModel\)", line.strip())
            if m:
                current = m.group(1)
                result[current] = []
            elif current:
                field_m = re.match(r"^\s{4}(\w+)\s*:", line)
                if field_m:
                    result[current].append(field_m.group(1))
                elif line.strip() and not line.startswith((" ", "\t")):
                    current = None
    except Exception:
        pass
    return result


def _format_api_result(method: str, path: str, raw: str) -> str:
    """HTTP API 결과 → 사용자 친화적 한국어 텍스트."""
    parts = raw.split("\n", 1)
    status_line = parts[0]  # e.g. "HTTP 201"
    body = parts[1].strip() if len(parts) > 1 else ""
    try:
        status_code = int(status_line.split()[1])
    except (IndexError, ValueError):
        status_code = 0
    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        data = {}

    method = method.upper()
    if 200 <= status_code < 300:
        if method == "DELETE":
            return "✅ 삭제가 완료되었습니다."
        if method == "GET":
            # find first list value: supports "items", "addons", "data", "results", etc.
            items = None
            total = None
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, list):
                        items = v
                        break
                total = data.get("total")
            if items is not None:
                if total is None:
                    total = len(items)
                _skip = {"is_deleted", "created_at", "updated_at", "password"}
                rows = "\n".join(
                    "  • " + ", ".join(
                        f"{k}: {v}" for k, v in (item.items() if isinstance(item, dict) else {}.items())
                        if v not in (None, "", False) and k not in _skip
                    )
                    for item in (items[:10] if isinstance(items, list) else [])
                )
                return f"✅ 조회 결과 (총 {total}건):\n{rows}" if rows else f"✅ 조회 결과: {total}건"
            return f"✅ 조회 완료:\n{body[:500]}"
        # POST / PATCH
        verb = "등록" if method == "POST" else "수정"
        if isinstance(data, dict):
            fields = [f"{k}: {v}" for k, v in data.items() if k not in ("id", "created_at", "updated_at", "is_deleted", "password") and v not in (None, "", False)]
            detail = "\n".join(f"  • {f}" for f in fields[:6])
            return f"✅ {verb}이 완료되었습니다.\n{detail}" if detail else f"✅ {verb}이 완료되었습니다."
        return f"✅ {verb}이 완료되었습니다."
    else:
        detail = ""
        if isinstance(data, dict):
            detail = data.get("detail") or data.get("message") or ""
        return f"❌ 오류 발생 (HTTP {status_code}): {detail or body[:200]}"


async def _addon_api_specs() -> str:
    """Active addon agents + their REST endpoints (from AST-parsed router prefix)."""
    try:
        from app.db import fetch_all
        rows = await fetch_all(
            "SELECT agent_key, agent_name, api_prefix, router_path, agent_type "
            "FROM tbl_addon_agents WHERE is_active = 1"
        )
        if not rows:
            return ""
        lines = ["Addon Agent APIs — use the call_api tool (or <api_call> tag for Ollama) to interact:"]
        for a in rows:
            api_prefix = a["api_prefix"]
            name = a["agent_name"]
            router_path = a.get("router_path") or ""

            # tools 형 addon (관제/프록시) — CRUD 가 아니라 /tools 계약을 안내
            src = ""
            try:
                src = Path(router_path).read_text(encoding="utf-8") if router_path else ""
            except Exception:
                pass
            if "/tools/{tool_name}" in src:
                import re as _re
                tool_names = _re.findall(r'"name":\s*"(\w+)"', src)
                lines.append(f"  [{name}] base: {api_prefix} (tool-style, read-only)")
                lines.append(f"    GET    {api_prefix}/tools                    — list tools")
                lines.append(
                    f"    POST   {api_prefix}/tools/{{tool_name}} body={{...arguments}}  — run tool"
                    + (f" (tools: {', '.join(tool_names[:5])})" if tool_names else "")
                )
                continue

            sub_prefix = _parse_router_prefix(router_path) if router_path else ""
            base = api_prefix + sub_prefix  # e.g. /api/addon/usermanager/users
            logger.debug("[orchestrator] addon spec: %s → %s", name, base)
            models = _parse_create_model_fields(router_path) if router_path else {}
            # pick the first XxxCreate model for POST body hint
            create_fields = next(
                (v for k, v in models.items() if k.endswith("Create")), []
            )
            update_fields = next(
                (v for k, v in models.items() if k.endswith("Update")), []
            )
            create_hint = (
                f" body={{{', '.join(f'\"{f}\":...' for f in create_fields)}}}"
                if create_fields else ""
            )
            update_hint = (
                f" body={{{', '.join(f'\"{f}\":...' for f in update_fields)}}}"
                if update_fields else ""
            )
            lines.append(f"  [{name}] base: {base}")
            lines.append(f"    GET    {base}                 — list/search")
            lines.append(f"    POST   {base}{create_hint}  — create")
            lines.append(f"    PATCH  {base}/{{id}}{update_hint}  — update")
            lines.append(f"    DELETE {base}/{{id}}            — delete")
        return "\n".join(lines)
    except Exception as exc:
        logger.error("[orchestrator] _addon_api_specs 오류: %s", exc)
        return ""


_CLASSIFY_SYSTEM = (
    "Analyze the user message and return the most applicable category as a JSON array.\n"
    "Return ONLY a JSON array, no other text. Example: [\"general\"]\n"
    "Rules:\n"
    "- Use 'gpu_monitoring' for: GPU status, utilization, VRAM/memory, temperature, power, "
    "XID/ECC errors, GPU alerts, GPU anomaly analysis.\n"
    "- Use 'hardware' for: server hardware status, CPU/memory of nodes, RAID, disk, "
    "PSU/power supply, fan, sensor temperature, BMC.\n"
    "- Use 'log_analysis' for: system/kernel(dmesg)/BMC log search, error log investigation, "
    "log pattern analysis ('로그 찾아줘', 'Xid 로그', '에러 로그').\n"
    "- Use 'trace_analysis' for: distributed traces, pipeline latency/bottleneck, span/trace "
    "investigation ('트레이스', '지연 분석', '파이프라인 병목').\n"
    "- Use 'storage' for: disk latency/IOPS, SMART/NVMe health, RAID array status "
    "('디스크', '스토리지', 'SMART', 'RAID').\n"
    "- Use 'bmc' for: BMC/iDRAC/iLO/IPMI sensors and events — fan speed, voltage rails, PSU, "
    "chassis power, inlet temp ('팬', '전압', 'PSU', 'BMC', 'IPMI', '섀시').\n"
    "- Use 'gpu_profiling' for: advanced GPU profiling — SM occupancy, Tensor core utilization, "
    "DRAM bandwidth, clock throttling, PCIe throughput, kernel efficiency "
    "('SM occupancy', 'Tensor', 'throttle', 'PCIe 대역폭', '커널 효율').\n"
    "- Use 'capacity_planning' for: underutilized GPUs, long-term utilization trends, efficiency "
    "reports, cardinality/storage cost governance ('저활용', '용량 계획', '효율 리포트', '카디널리티', '비용').\n"
    "- Use 'anomaly_detection' for: statistical anomaly detection on metrics, alert correlation, "
    "root cause investigation ('이상 탐지', '이상치', '알람 상관', '원인 분석').\n"
    "- Use 'network' for: NIC errors/drops, link status, interface throughput "
    "('네트워크', 'NIC', '인터페이스', '링크 다운', '패킷 드롭').\n"
    "- Use 'workload_correlation' for: which job/user/process is using which GPU, "
    "per-job or per-user GPU memory usage ('어떤 잡', '누가 사용', '프로세스별 GPU', 'job_id').\n"
    "- A question spanning multiple layers (e.g. node overall health) may return several.\n"
    "- Use 'general' for: platform data operations (agents/users/settings CRUD), "
    "casual conversation, anything else.\n"
    "When in doubt, use 'general'.\n"
    "Valid categories: " + ", ".join(_VALID_INTENTS)
)

_PLATFORM_BASE_SYSTEM = """\
당신은 CoreSight-G GPU·서버 관제 플랫폼의 AI 어시스턴트입니다.

## 역할 및 책임
- 현재 플랫폼에서 활성화된 에이전트와 기능을 기반으로만 답변합니다.
- 플랫폼에 존재하지 않는 기능·외부 서비스·비활성 에이전트에 대한 정보를 제공하지 않습니다.
- 지원하지 않는 요청에는 "현재 플랫폼에서 지원하지 않는 기능입니다."라고 답변합니다.

## 데이터 정확성 원칙 (환각 방지)
- 사용자가 데이터 조회·생성·수정·삭제를 요청하면 반드시 call_api 도구를 호출하여 실제 API로 처리합니다.
- API 호출 없이 데이터를 지어내거나 가정하여 응답하지 않습니다.
- API 응답 결과를 그대로 사용자에게 전달하며, 임의로 수정하거나 보완하지 않습니다.
- 오류 응답(4xx, 5xx)이 반환되면 사용자에게 정확한 오류 내용을 알립니다.

## 응답 원칙
- 기본 응답 언어는 한국어이며, 사용자 언어에 따라 조정합니다.
- 확인되지 않은 정보·불확실한 사실은 절대 제공하지 않습니다.
- 간결하고 명확한 답변을 제공하며, 불필요한 설명을 반복하지 않습니다.

---

You are the AI assistant of the CoreSight-G Platform.

## Role & Responsibilities
- Answer ONLY based on features and agents that are currently active on this platform.
- Do NOT provide information about non-existent features, external services, or disabled agents.
- For unsupported requests, respond: "This feature is not supported on the current platform."

## Data Accuracy Principles (Anti-Hallucination)
- When users request data operations (read/create/update/delete), you MUST call the call_api tool to invoke the actual API.
- Never fabricate or assume data without first making an actual API call.
- Relay API responses exactly as received; do not modify or supplement them.
- If the API returns an error (4xx/5xx), report the exact error to the user.

## Response Principles
- Default response language is Korean; adapt to the user's language.
- Never provide unverified or uncertain information.
- Be concise and clear; avoid unnecessary repetition.\
"""


async def _build_system_prompt(user_id: str | None = None) -> str:
    """플랫폼 제한 + 활성 에이전트 목록 + 시스템/사용자 맞춤지침 조합."""
    from app.db import fetch_all, fetch_one, _PH as _PH_
    parts = [_PLATFORM_BASE_SYSTEM]

    try:
        agent_rows = await fetch_all(
            "SELECT agent_name FROM tbl_agent_config WHERE is_enabled = 1 ORDER BY sort_order"
        )
        names = [r["agent_name"] for r in agent_rows]
        if names:
            parts.append(f"Currently active agents: {', '.join(names)}")
    except Exception:
        pass

    addon_spec = await _addon_api_specs()
    if addon_spec:
        parts.append(addon_spec)
        parts.append(
            "IMPORTANT: When the user requests any action (add/create/edit/delete/list/search) "
            "on an addon agent, you MUST use the call_api tool to actually perform it. "
            "Never fabricate API responses or pretend an action was performed."
        )

    try:
        sys_row = await fetch_one(
            "SELECT value FROM tbl_settings WHERE key = 'system_custom_instructions'"
        )
        if sys_row and sys_row.get("value"):
            parts.append(f"[시스템 맞춤지침 / System Instructions]\n{sys_row['value']}")
    except Exception:
        pass

    try:
        usr_common_row = await fetch_one(
            "SELECT value FROM tbl_settings WHERE key = 'user_custom_instructions'"
        )
        if usr_common_row and usr_common_row.get("value"):
            parts.append(f"[사용자 공통 맞춤지침 / User Common Instructions]\n{usr_common_row['value']}")
    except Exception:
        pass

    if user_id:
        try:
            user_row = await fetch_one(
                f"SELECT custom_instructions FROM tbl_users WHERE user_id = {_PH_}",
                (user_id,),
            )
            if user_row and user_row.get("custom_instructions"):
                parts.append(f"[User Instructions]\n{user_row['custom_instructions']}")
        except Exception:
            pass

    return "\n\n".join(parts)


async def _disabled_agents() -> set[str]:
    """비활성 intent 집합 — tbl_agent_config(is_enabled=0) + Addon 에이전트(is_active=0).

    Addon 에이전트(P1~, agent_config 행 없음)는 tbl_addon_agents.is_active 를
    addon_key → intent 역매핑(_AGENT_MAP)으로 반영. DB 조회 실패 시 빈 세트.
    """
    disabled: set[str] = set()
    try:
        from app.db import fetch_all
        rows = await fetch_all(
            "SELECT agent_key FROM tbl_agent_config WHERE is_enabled = 0"
        )
        disabled |= {r["agent_key"] for r in rows}

        addon_rows = await fetch_all(
            "SELECT agent_key FROM tbl_addon_agents WHERE is_active = 0"
        )
        inactive_addons = {r["agent_key"] for r in addon_rows}
        for intent, cls in _AGENT_MAP.items():
            if getattr(cls, "addon_key", None) in inactive_addons:
                disabled.add(intent)
    except Exception:
        pass
    return disabled


_SETTING_ENV_MAP = {
    "orchestrator_model": "ORCHESTRATOR_MODEL",
    "domain_agent_model": "DOMAIN_AGENT_MODEL",
    "ollama_base_url": "OLLAMA_BASE_URL",
    "ollama_model": "OLLAMA_MODEL",
}


async def _db_llm_settings() -> dict[str, str]:
    """LLM 설정 — 우선순위: os.environ > .env.* 파일 > tbl_settings DB > 기본값.

    우선순위 상세:
    1. os.environ  : Docker Compose environment:/env_file: 로 주입된 값 (최우선)
    2. .env.* 파일 : pydantic-settings 가 로드한 값 (.env.local 등) — 기본값과 다를 때만 적용
    3. tbl_settings: Setup Wizard/UI 에서 저장한 DB 값
    4. 기본값       : config.py 하드코딩 기본

    pydantic-settings 는 .env 파일을 settings 객체에만 로드하고 os.environ 에는 주입하지
    않으므로, settings 객체 값이 기본값과 다를 때는 .env 에서 명시된 것으로 판단해 DB를 덮어쓴다.
    """
    import os
    from app.core.config import settings as _settings

    # pydantic config.py 기본값 (이와 다르면 .env 에서 명시 설정된 것)
    _pydantic_defaults = {
        "ollama_model": "llama3.2",
        "ollama_base_url": "http://localhost:11434",
        "orchestrator_model": "claude-sonnet-4-6",
        "domain_agent_model": "claude-haiku-4-5-20251001",
    }
    _settings_vals = {
        "ollama_model": _settings.ollama_model,
        "ollama_base_url": _settings.ollama_base_url,
        "orchestrator_model": _settings.orchestrator_model,
        "domain_agent_model": _settings.domain_agent_model,
    }

    # 1단계: DB 값 로드
    try:
        from app.db import fetch_all
        rows = await fetch_all(
            "SELECT key, value FROM tbl_settings WHERE key IN "
            "('ollama_base_url','ollama_model','orchestrator_model','domain_agent_model')"
        )
        result = {r["key"]: r["value"] for r in rows if r.get("value")}
    except Exception:
        result = {}

    # 2단계: pydantic settings 값이 기본값과 다르면 .env.* 에서 명시된 것 → DB 덮어쓰기
    for key, val in _settings_vals.items():
        if val and val != _pydantic_defaults.get(key):
            result[key] = val

    # 3단계: os.environ 명시 시 최우선 (Docker Compose environment:/env_file: 주입)
    for db_key, env_key in _SETTING_ENV_MAP.items():
        val = os.environ.get(env_key)
        if val:
            result[db_key] = val

    return result


# ── F25: Orchestrator 고도화 ──────────────────────────────────────────────────

_HIGH_RISK_INTENTS: set[str] = {"delete", "deploy", "execute", "approve"}


async def _get_setting_bool(key: str, default: bool = False) -> bool:
    """tbl_settings bool 설정 조회 (true/1/yes → True)."""
    from app.db import fetch_one, _PH
    try:
        row = await fetch_one(f"SELECT value FROM tbl_settings WHERE key = {_PH}", (key,))
        if row and row.get("value"):
            return str(row["value"]).lower() in ("true", "1", "yes")
        return default
    except Exception:
        return default


async def _registry_find_by_verb(verb: str) -> list[dict]:
    """tbl_addon_agent_capabilities 에서 verb 일치 활성 addon 검색."""
    from app.db import fetch_all, _PH
    try:
        return await fetch_all(
            f"SELECT a.agent_key, a.agent_name, a.agent_type, a.api_prefix "
            f"FROM tbl_addon_agents a "
            f"JOIN tbl_addon_agent_capabilities c ON a.agent_key = c.agent_key "
            f"WHERE c.verb = {_PH} AND a.is_active = 1",
            (verb,),
        )
    except Exception:
        return []


async def _find_agent_by_type(agent_type: str) -> dict | None:
    """활성 addon 중 agent_type 일치 첫 번째 항목 반환."""
    from app.db import fetch_one, _PH
    try:
        return await fetch_one(
            f"SELECT agent_key, agent_name, api_prefix "
            f"FROM tbl_addon_agents WHERE agent_type = {_PH} AND is_active = 1",
            (agent_type,),
        )
    except Exception:
        return None


async def _call_reviewer_gate(response_text: str, token: str | None) -> dict:
    """Reviewer addon /review 엔드포인트 호출 → 품질 검수 결과."""
    reviewer = await _find_agent_by_type("reviewer")
    if not reviewer:
        return {"reviewed": False}
    api_prefix = reviewer.get("api_prefix", "")
    if not api_prefix:
        return {"reviewed": False}
    try:
        raw = await _exec_api_call(
            "POST",
            f"{api_prefix}/review",
            {"content": response_text},
            None,
            token,
        )
        parts = raw.split("\n", 1)
        status_code = int(parts[0].split()[1])
        if 200 <= status_code < 300 and len(parts) > 1:
            data = json.loads(parts[1])
            return {
                "reviewed": True,
                "verdict": data.get("verdict", "approved"),
                "score": float(data.get("score", 1.0)),
                "issues": data.get("issues", []),
            }
        return {"reviewed": False}
    except Exception:
        return {"reviewed": False}


class Orchestrator:
    def __init__(self) -> None:
        self._key = settings.anthropic_api_key
        self._client: anthropic.AsyncAnthropic | None = (
            anthropic.AsyncAnthropic(api_key=self._key) if self._key else None
        )

    def _use_ollama(self, model: str | None) -> bool:
        """Ollama 경로 사용 여부: 명시적 ollama 선택 OR Anthropic key 없음."""
        return model == "ollama" or not self._key

    async def _classify_intent(self, user_message: str) -> list[str]:
        if not self._client:
            return ["general"]
        try:
            db = await _db_llm_settings()
            orch_model = db.get("orchestrator_model") or settings.orchestrator_model
            resp = await self._client.messages.create(
                model=orch_model,
                max_tokens=30,
                system=_CLASSIFY_SYSTEM,
                messages=[{"role": "user", "content": user_message}],
            )
            intents: list[str] = json.loads(resp.content[0].text.strip())
            disabled = await _disabled_agents()
            valid = [
                i for i in intents
                if i in _VALID_INTENTS and (i == "general" or i not in disabled)
            ]
            result = valid or ["general"]
            logger.warning("[orchestrator] intent: %s → %s", intents, result)
            return result
        except Exception as exc:
            logger.warning("[orchestrator] intent 분류 실패, general 폴백: %s", exc)
            return ["general"]

    def _make_agent(self, intent: str) -> Any | None:
        cls = _AGENT_MAP.get(intent)
        if cls is None:
            return None
        if isinstance(cls, str) and cls.startswith("a2a://"):
            return None
        return cls()

    async def _claude_general(self, user_message: str, history: list[dict], system_prompt: str) -> str:
        return await self._claude_with_tools(user_message, history, system_prompt, token=None)

    async def _claude_with_tools(
        self,
        user_message: str,
        history: list[dict],
        system_prompt: str,
        token: str | None = None,
    ) -> str:
        if not self._client:
            raise RuntimeError("Anthropic client not configured")
        db = await _db_llm_settings()
        orch_model = db.get("orchestrator_model") or settings.orchestrator_model
        messages = list(history) + [{"role": "user", "content": user_message}]

        for _ in range(6):  # max 6 tool-call rounds
            resp = await self._client.messages.create(
                model=orch_model,
                max_tokens=2048,
                system=system_prompt,
                messages=messages,
                tools=[_TOOL_CALL_API],
            )
            if resp.stop_reason != "tool_use":
                return "".join(
                    b.text for b in resp.content if hasattr(b, "text")
                )
            messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    inp = block.input
                    result = await _exec_api_call(
                        inp.get("method", "GET"),
                        inp.get("path", ""),
                        inp.get("body"),
                        inp.get("params"),
                        token,
                    )
                    logger.warning("[orchestrator] tool call_api %s %s → %s", inp.get("method"), inp.get("path"), result[:120])
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})

        return "처리 중 오류가 발생했습니다. 다시 시도해 주세요."

    async def _ollama_general(self, user_message: str, history: list[dict], system_prompt: str) -> str:
        db = await _db_llm_settings()
        messages = list(history) + [{"role": "user", "content": user_message}]
        return await call_ollama(
            messages,
            system_prompt,
            model=db.get("ollama_model"),
            base_url=db.get("ollama_base_url"),
        )

    async def _ollama_with_tools(
        self,
        user_message: str,
        history: list[dict],
        system_prompt: str,
        token: str | None = None,
    ) -> str:
        """Ollama용 prompt-based tool calling: <api_call>JSON</api_call> 태그 파싱."""
        import re as _re

        db = await _db_llm_settings()
        _model = db.get("ollama_model")
        _base_url = db.get("ollama_base_url")

        # Extract only the addon API specs section for Ollama (short & focused)
        addon_spec = await _addon_api_specs()
        ollama_sys = (
            "You are an AI assistant. Respond in Korean.\n\n"
            "## CRITICAL RULE: API CALLS\n"
            "To perform any data operation, output EXACTLY this tag (nothing else on the line):\n"
            "<api_call>{\"method\":\"METHOD\",\"path\":\"/path\",\"body\":{...}}</api_call>\n"
            "Do NOT write the result yourself. Wait for the real API response.\n"
            "Do NOT hallucinate endpoints. ONLY use paths listed below.\n\n"
            "## Built-in System APIs\n"
            "  GET  /api/agent-config/           — list ALL agents (built-in + addon, full config)\n"
            "  GET  /api/addon-agents/            — list addon-only agents (upload/toggle management)\n\n"
            "## Examples\n"
            "User: 에이전트 목록 보여줘\n"
            "Assistant: <api_call>{\"method\":\"GET\",\"path\":\"/api/agent-config/\"}</api_call>\n\n"
            "User: 사용 가능한 에이전트 알려줘\n"
            "Assistant: <api_call>{\"method\":\"GET\",\"path\":\"/api/agent-config/\"}</api_call>\n\n"
            "User: usermanager에 hong 사용자 추가\n"
            "Assistant: <api_call>{\"method\":\"POST\",\"path\":\"/api/addon/usermanager/users\","
            "\"body\":{\"username\":\"hong\",\"role\":\"user\"}}</api_call>\n\n"
            "User: 안녕?\n"
            "Assistant: 안녕하세요!\n\n"
        )
        if addon_spec:
            ollama_sys += "## Available APIs (exact paths and fields)\n" + addon_spec + "\n\n"
        # Append any custom instructions from the full prompt (last section only)
        custom_parts = [p for p in system_prompt.split("\n\n") if "맞춤지침" in p or "instruction" in p.lower()]
        if custom_parts:
            ollama_sys += "\n".join(custom_parts)

        messages: list[dict] = list(history) + [{"role": "user", "content": user_message}]

        for rnd in range(6):
            text = await call_ollama(messages, ollama_sys, model=_model, base_url=_base_url)
            logger.warning("[orchestrator] ollama round %d response: %.120s", rnd, text)

            # Try strict match first, fallback to brace-counting (handles missing </api_call>)
            match = _re.search(r"<api_call>\s*(.*?)\s*</api_call>", text, _re.DOTALL)
            if not match:
                # Extract JSON by finding <api_call> + first complete {…} object
                tag_idx = text.find("<api_call>")
                if tag_idx == -1:
                    return text  # 일반 텍스트 응답
                json_start = text.find("{", tag_idx)
                if json_start == -1:
                    return text
                depth = 0
                json_end = -1
                for ci, ch in enumerate(text[json_start:]):
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            json_end = json_start + ci + 1
                            break
                if json_end == -1:
                    return text
                json_str = text[json_start:json_end]
            else:
                json_str = match.group(1)

            try:
                call = json.loads(json_str)
                result = await _exec_api_call(
                    call.get("method", "GET"),
                    call.get("path", ""),
                    call.get("body"),
                    call.get("params"),
                    token,
                )
                logger.warning(
                    "[orchestrator] ollama api_call %s %s → %s",
                    call.get("method"), call.get("path"), result[:200],
                )
                # On 4xx/5xx, feed error back so Ollama can self-correct
                status_line = result.split("\n", 1)[0]
                try:
                    status_code = int(status_line.split()[1])
                except (IndexError, ValueError):
                    status_code = 0
                if 400 <= status_code < 600:
                    messages.append({"role": "assistant", "content": text})
                    messages.append({"role": "user", "content": f"API 오류: {result[:300]}\n위 요청을 수정하여 다시 시도해 주세요."})
                    continue
                return _format_api_result(call.get("method", ""), call.get("path", ""), result)
            except Exception as exc:
                logger.warning("[orchestrator] ollama api_call 파싱 실패: %s", exc)
                return text

        return text

    async def _synthesize(self, results: dict[str, str], user_message: str) -> str:
        if not self._client:
            return "\n\n".join(f"[{_AGENT_LABELS.get(k, k)}]\n{v}" for k, v in results.items())
        db = await _db_llm_settings()
        orch_model = db.get("orchestrator_model") or settings.orchestrator_model
        combined = "\n\n".join(
            f"[{_AGENT_LABELS.get(k, k)}]\n{v}" for k, v in results.items()
        )
        try:
            resp = await self._client.messages.create(
                model=orch_model,
                max_tokens=2048,
                system="Synthesize multiple agent responses into a clear, unified final answer for the user.",
                messages=[{"role": "user", "content": f"Original question: {user_message}\n\n{combined}"}],
            )
            return resp.content[0].text
        except Exception:
            return combined

    async def run(
        self, user_message: str, history: list[dict], model: str | None = None,
        user_id: str | None = None, token: str | None = None,
    ) -> str:
        logger.warning("[orchestrator] run() called, msg=%.40s", user_message)
        rule = await match_rule_async(user_message)
        if rule:
            action = rule.get("action", {})
            if action.get("type") == "api_call":
                raw = await _exec_api_call(action["method"], action["path"], None, None, token)
                return await format_response(rule, raw)
            if action.get("type") == "disabled_check":
                return await format_response(rule, "")
        sys_prompt = await _build_system_prompt(user_id)
        if self._use_ollama(model):
            return await self._ollama_with_tools(user_message, history, sys_prompt, token=token)

        intents = await self._classify_intent(user_message)
        if len(intents) == 1:
            agent = self._make_agent(intents[0])
            if agent:
                return await agent.run(user_message, history)
            try:
                return await self._claude_with_tools(user_message, history, sys_prompt, token=token)
            except Exception as exc:
                logger.warning("[orchestrator] Claude 실패, Ollama 폴백: %s", exc)
                return await self._ollama_with_tools(user_message, history, sys_prompt, token=token)

        tasks = []
        for intent in intents:
            agent = self._make_agent(intent)
            if agent:
                tasks.append((intent, agent.run(user_message, history)))
        if not tasks:
            return await self._ollama_with_tools(user_message, history, sys_prompt, token=token)

        results_list = await asyncio.gather(*[t for _, t in tasks])
        results = {intent: r for (intent, _), r in zip(tasks, results_list)}
        return await self._synthesize(results, user_message)

    async def stream(
        self, user_message: str, history: list[dict], model: str | None = None,
        user_id: str | None = None, token: str | None = None,
    ) -> AsyncGenerator[str, None]:
        logger.warning("[orchestrator] stream() called, msg=%.40s", user_message)
        try:
            rule = await match_rule_async(user_message)
            if rule:
                import re as _re
                action = rule.get("action", {})
                rule_text: str | None = None
                if action.get("type") == "disabled_check":
                    rule_text = await format_response(rule, "")
                elif action.get("type") == "api_call":
                    raw = await _exec_api_call(action["method"], action["path"], None, None, token)
                    rule_text = await format_response(rule, raw)
                if rule_text is not None:
                    yield f"event: intent\ndata: {json.dumps({'intents': ['keyword_rule']})}\n\n"
                    yield f"event: agent_start\ndata: {json.dumps({'agent': rule['id'], 'label': rule.get('description', rule['id'])})}\n\n"
                    for tok in _re.findall(r"\S+|\s+", rule_text):
                        yield f"event: delta\ndata: {json.dumps({'text': tok})}\n\n"
                        if not tok.isspace():
                            await asyncio.sleep(0.03)
                    yield "event: done\ndata: {}\n\n"
                    return
            sys_prompt = await _build_system_prompt(user_id)

            # ── Ollama 경로 (명시적 선택 또는 Anthropic key 없음) ──────────
            if self._use_ollama(model):
                yield f"event: intent\ndata: {json.dumps({'intents': ['general']})}\n\n"
                yield f"event: agent_start\ndata: {json.dumps({'agent': 'general', 'label': '일반 응답 (Ollama)'})}\n\n"
                text = await self._ollama_with_tools(user_message, history, sys_prompt, token=token)
                yield f"event: delta\ndata: {json.dumps({'text': text})}\n\n"
                yield "event: done\ndata: {}\n\n"
                return

            # ── Claude 경로 ────────────────────────────────────────────────
            intents = await self._classify_intent(user_message)
            yield f"event: intent\ndata: {json.dumps({'intents': intents})}\n\n"

            # F25-1: capability 기반 Registry 검색 (옵트인)
            if await _get_setting_bool("registry_dynamic_routing"):
                for intent in intents:
                    if intent not in _AGENT_MAP:
                        candidates = await _registry_find_by_verb(intent)
                        yield (
                            f"event: registry_miss\ndata: {json.dumps({'type': 'registry_miss', 'intent': intent, 'candidates': [c['agent_key'] for c in candidates], 'fallback': 'general'})}\n\n"
                        )

            # F25-3: HITL 게이트 (옵트인)
            if await _get_setting_bool("hitl_gate_enabled"):
                for intent in intents:
                    if intent in _HIGH_RISK_INTENTS:
                        hitl = await _find_agent_by_type("hitl")
                        if hitl:
                            import uuid as _uuid
                            approval_id = str(_uuid.uuid4())
                            yield (
                                f"event: hitl_pending\ndata: {json.dumps({'type': 'hitl_pending', 'approval_id': approval_id, 'intent': intent, 'message': '승인 대기 중'})}\n\n"
                            )
                            yield "event: done\ndata: {}\n\n"
                            return

            # 응답 수집 (F25-2 reviewer gate 적용 시 텍스트 모아야 함)
            reviewer_gate = await _get_setting_bool("reviewer_gate_enabled")
            for intent in intents:
                yield f"event: agent_start\ndata: {json.dumps({'agent': intent, 'label': _AGENT_LABELS.get(intent, intent)})}\n\n"
                agent = self._make_agent(intent)

                if agent and hasattr(agent, "stream"):
                    async for chunk in agent.stream(user_message, history):
                        yield chunk
                else:
                    try:
                        text = await self._claude_with_tools(user_message, history, sys_prompt, token=token)
                    except Exception as exc:
                        logger.warning("[orchestrator] Claude 실패, Ollama 폴백: %s", exc)
                        text = await self._ollama_with_tools(user_message, history, sys_prompt, token=token)

                    # F25-2: reviewer gate (옵트인)
                    if reviewer_gate:
                        review = await _call_reviewer_gate(text, token)
                        if review.get("reviewed"):
                            yield (
                                f"event: review_gate\ndata: {json.dumps({'type': 'review_gate', 'verdict': review.get('verdict', 'approved'), 'score': review.get('score', 1.0)})}\n\n"
                            )
                            if review.get("verdict") == "rejected":
                                issues = review.get("issues", [])
                                yield f"event: delta\ndata: {json.dumps({'text': f'[품질 검수 반려] {issues}'})}\n\n"
                                yield "event: done\ndata: {}\n\n"
                                return

                    yield f"event: delta\ndata: {json.dumps({'text': text})}\n\n"

            yield "event: done\ndata: {}\n\n"

        except Exception as exc:
            logger.error("[orchestrator] 스트림 오류: %s", exc)
            yield f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n"
