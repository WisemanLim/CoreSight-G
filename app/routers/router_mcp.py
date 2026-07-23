"""MCP JSON-RPC 2.0 endpoint — Hybrid/Standalone mode (F12).

Spec: https://spec.modelcontextprotocol.io (2025-11-05)
Transport: Streamable HTTP (POST /mcp, POST /mcp/{agent_key})

각 Addon Agent가 개별 MCP 서버로 동작:
  POST /mcp/{agent_key}            — per-agent MCP JSON-RPC 2.0
  GET  /mcp/{agent_key}/guide      — per-agent 가이드 + 클라이언트 설정
  POST /mcp                        — 전체 통합 엔드포인트 (모든 active addon tools)
  GET  /mcp/guide                  — 전체 가이드
"""
import json
import logging
import random
import re
import socket

import httpx
from fastapi import APIRouter, Request

logger = logging.getLogger("uvicorn.error")
router = APIRouter(tags=["mcp"])


def _get_server_host() -> str:
    """Detect LAN IP of this server (not localhost) for MCP URL generation."""
    from app.core.config import settings
    if settings.mcp_host:
        return settings.mcp_host
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "localhost"


def _ok(id_: object, result: object) -> dict:
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def _err(id_: object, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}


async def _fetch_openapi_spec() -> dict:
    from app.main import app as _app
    transport = httpx.ASGITransport(app=_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as c:
        resp = await c.get("/openapi.json")
        return resp.json() if resp.status_code == 200 else {}


async def _get_addon_tools() -> list[dict]:
    """전체 활성 Addon → MCP tool list."""
    from app.addon_agent_loader import _active_prefixes
    from app.services.openapi_to_mcp import openapi_to_mcp_tools

    if not _active_prefixes:
        return []
    spec = await _fetch_openapi_spec()
    if not spec:
        return []
    tools: list[dict] = []
    for prefix in _active_prefixes:
        tools.extend(openapi_to_mcp_tools(spec, path_prefix_filter=prefix))
    return tools


async def _get_agent_tools(agent_key: str) -> tuple[list[dict], str | None]:
    """특정 agent_key의 MCP tool list + prefix 반환 (addon + builtin 공통 지원)."""
    try:
        from app.db import fetch_one, _PH

        # 1. Addon agent — api_prefix 기반 OpenAPI 필터
        addon_row = await fetch_one(
            f"SELECT api_prefix FROM tbl_addon_agents WHERE agent_key = {_PH} AND is_active = 1",
            (agent_key,),
        )
        if addon_row:
            prefix: str = addon_row["api_prefix"]
            from app.addon_agent_loader import _active_prefixes
            if prefix not in _active_prefixes:
                return [], None
            spec = await _fetch_openapi_spec()
            if not spec:
                return [], None
            from app.services.openapi_to_mcp import openapi_to_mcp_tools
            return openapi_to_mcp_tools(spec, path_prefix_filter=prefix), prefix

        # 2. Builtin 에이전트 — is_enabled 확인, tool 없이 alive 표시만
        builtin_row = await fetch_one(
            f"SELECT agent_key FROM tbl_agent_config WHERE agent_key = {_PH} AND is_enabled = 1 AND is_required = 0",
            (agent_key,),
        )
        if builtin_row:
            return [], agent_key  # tool 없음, alive=True

    except Exception:
        pass

    return [], None


async def _exec_addon_tool(tool: dict, input_args: dict, auth_header: str) -> str:
    from app.main import app as _app

    meta = tool.get("_meta", {})
    method = meta.get("method", "GET")
    path = meta.get("path", "")
    args = dict(input_args)

    path = re.sub(r"\{([^}]+)\}", lambda m: str(args.pop(m.group(1), m.group(0))), path)
    headers = {"Authorization": auth_header} if auth_header else {}

    transport = httpx.ASGITransport(app=_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as c:
        fn = getattr(c, method.lower())
        kwargs: dict = {"headers": headers}
        if method in ("GET", "HEAD", "DELETE"):
            kwargs["params"] = args
        else:
            kwargs["json"] = args
        try:
            resp = await fn(path, **kwargs)
            return f"HTTP {resp.status_code}\n{resp.text}"
        except Exception as exc:
            return f"HTTP ERROR\n{json.dumps({'error': str(exc)})}"


def _client_configs(agent_key: str, mcp_url: str) -> dict:
    return {
        "claude_desktop": {
            "description": "~/.config/claude/claude_desktop_config.json 에 추가",
            "config": {"mcpServers": {agent_key: {"type": "http", "url": mcp_url}}},
        },
        "cursor": {
            "description": ".cursor/mcp.json 에 추가",
            "config": {"mcpServers": {agent_key: {"type": "http", "url": mcp_url}}},
        },
        "vscode_continue": {
            "description": ".continue/config.json mcp 섹션에 추가",
            "config": {"name": agent_key, "transport": {"type": "http", "url": mcp_url}},
        },
    }


# ── Per-agent endpoints ───────────────────────────────────────────────────────

@router.get("/mcp/guide")
async def mcp_guide(request: Request):
    """전체 통합 MCP 가이드 (모든 활성 addon tools)."""
    from urllib.parse import urlparse
    server_host = _get_server_host()
    parsed = urlparse(str(request.base_url))
    port_part = f":{parsed.port}" if parsed.port else ""
    mcp_url = f"http://{server_host}{port_part}/mcp"
    tools = await _get_addon_tools()
    return {
        "mcp_url": mcp_url,
        "transport": "Streamable HTTP (POST)",
        "protocol": "MCP JSON-RPC 2.0 (2025-11-05)",
        "active_tools_count": len(tools),
        "active_tools": [{"name": t["name"], "description": t["description"]} for t in tools],
        "client_configs": _client_configs("wise-multiagent", mcp_url),
    }


@router.get("/mcp/{agent_key}/guide")
async def mcp_agent_guide(agent_key: str, request: Request):
    """Per-agent MCP 가이드 — 활성 상태·tool 목록·클라이언트 설정 스니펫."""
    tools, prefix = await _get_agent_tools(agent_key)

    # MCP config 확인 — proxy port 있으면 사용, 없으면 자동 할당 후 저장
    proxy_port: int | None = None
    try:
        from app.db import fetch_one, fetch_all, execute_write, _PH as _PH2
        cfg = await fetch_one(
            f"SELECT port FROM tbl_mcp_configs WHERE agent_key = {_PH2} AND is_enabled = 1",
            (agent_key,),
        )
        if cfg and cfg["port"]:
            proxy_port = int(cfg["port"])
        else:
            # Auto-assign unused port in 20000-59999 range
            used = {r["port"] for r in await fetch_all("SELECT port FROM tbl_mcp_configs WHERE port IS NOT NULL")}
            while True:
                candidate = random.randint(20000, 59999)
                if candidate not in used:
                    proxy_port = candidate
                    break
            existing = await fetch_one(
                f"SELECT agent_key FROM tbl_mcp_configs WHERE agent_key = {_PH2}", (agent_key,)
            )
            if existing:
                await execute_write(
                    f"UPDATE tbl_mcp_configs SET port={_PH2}, is_enabled=1, updated_at=CURRENT_TIMESTAMP WHERE agent_key={_PH2}",
                    (proxy_port, agent_key),
                )
            else:
                await execute_write(
                    f"INSERT INTO tbl_mcp_configs (agent_key, port, extra_args, is_enabled) VALUES ({_PH2},{_PH2},'[]',1)",
                    (agent_key, proxy_port),
                )
    except Exception:
        pass

    # is_alive: proxy_port 있으면 TCP 연결 가능 여부로 판단 (standalone 지원)
    # proxy_port 없으면 main-app _active_prefixes 기준
    if proxy_port:
        try:
            with socket.create_connection(("localhost", proxy_port), timeout=1):
                is_alive = True
        except OSError:
            is_alive = False
    else:
        from app.addon_agent_loader import _active_prefixes
        is_alive = bool(prefix and (prefix in _active_prefixes or prefix == agent_key))

    server_host = _get_server_host()
    if proxy_port:
        mcp_url = f"http://{server_host}:{proxy_port}/mcp"
    else:
        from urllib.parse import urlparse
        base_url = str(request.base_url).rstrip("/")
        parsed = urlparse(base_url)
        port_part = f":{parsed.port}" if parsed.port else ""
        mcp_url = f"http://{server_host}{port_part}/mcp/{agent_key}"

    return {
        "agent_key": agent_key,
        "mcp_url": mcp_url,
        "proxy_port": proxy_port,
        "server_host": server_host,
        "is_alive": is_alive,
        "transport": "Streamable HTTP (POST)",
        "protocol": "MCP JSON-RPC 2.0 (2025-11-05)",
        "active_tools_count": len(tools),
        "active_tools": [{"name": t["name"], "description": t["description"]} for t in tools],
        "client_configs": _client_configs(agent_key, mcp_url),
    }


@router.post("/mcp/{agent_key}")
async def mcp_agent_endpoint(agent_key: str, body: dict, request: Request):
    """Per-agent MCP JSON-RPC 2.0 — 해당 agent의 API만 tool로 노출."""
    method = body.get("method", "")
    id_ = body.get("id")
    params = body.get("params", {})
    auth_header = request.headers.get("authorization", "")

    if method == "initialize":
        return _ok(id_, {
            "protocolVersion": params.get("protocolVersion", "2025-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": f"wise-agent-{agent_key}", "version": "1.0.0"},
        })

    tools, _ = await _get_agent_tools(agent_key)

    if method == "tools/list":
        return _ok(id_, {"tools": [
            {"name": t["name"], "description": t["description"],
             "inputSchema": t.get("inputSchema", {"type": "object", "properties": {}})}
            for t in tools
        ]})

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_input = params.get("arguments", {})
        addon_tool = next((t for t in tools if t["name"] == tool_name), None)
        if not addon_tool:
            return _err(id_, -32602, f"Unknown tool: {tool_name}")
        result = await _exec_addon_tool(addon_tool, tool_input, auth_header)
        return _ok(id_, {"content": [{"type": "text", "text": result}]})

    return _err(id_, -32601, f"Method not found: {method}")


# ── Global endpoint ───────────────────────────────────────────────────────────

@router.post("/mcp")
async def mcp_endpoint(body: dict, request: Request):
    """통합 MCP JSON-RPC 2.0 — 모든 활성 addon tools 노출."""
    method = body.get("method", "")
    id_ = body.get("id")
    params = body.get("params", {})
    auth_header = request.headers.get("authorization", "")

    if method == "initialize":
        return _ok(id_, {
            "protocolVersion": params.get("protocolVersion", "2025-11-05"),
            "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
            "serverInfo": {"name": "coresight-g", "version": "1.0.0"},
        })

    if method == "tools/list":
        addon_tools = await _get_addon_tools()
        mcp_tools = [
            {"name": t["name"], "description": t["description"],
             "inputSchema": t.get("inputSchema", {"type": "object", "properties": {}})}
            for t in addon_tools
        ]
        from app.agents.addon_tool_agent import addon_agent_cls
        for t in addon_agent_cls("gpu-monitor", "gpu_monitoring")().get_tools():
            mcp_tools.append({
                "name": t["name"],
                "description": t.get("description", ""),
                "inputSchema": t.get("input_schema", {"type": "object", "properties": {}}),
            })
        logger.info("[mcp] tools/list → %d tools", len(mcp_tools))
        return _ok(id_, {"tools": mcp_tools})

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_input = params.get("arguments", {})
        addon_tools = await _get_addon_tools()
        addon_tool = next((t for t in addon_tools if t["name"] == tool_name), None)
        if addon_tool:
            result = await _exec_addon_tool(addon_tool, tool_input, auth_header)
            return _ok(id_, {"content": [{"type": "text", "text": result}]})
        from app.agents.addon_tool_agent import addon_agent_cls
        executors = addon_agent_cls("gpu-monitor", "gpu_monitoring")().get_tool_executors()
        if tool_name not in executors:
            return _err(id_, -32602, f"Unknown tool: {tool_name}")
        try:
            result = await executors[tool_name](tool_input)
            return _ok(id_, {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]})
        except Exception as exc:
            return _err(id_, -32000, str(exc))

    if method == "resources/list":
        return _ok(id_, {"resources": [{"uri": "domain://context", "name": "Domain Context", "mimeType": "text/plain"}]})

    if method == "resources/read":
        uri = params.get("uri", "")
        if uri == "domain://context":
            from app.agents.addon_tool_agent import addon_agent_cls
            ctx = await addon_agent_cls("gpu-monitor", "gpu_monitoring")().build_domain_context()
            return _ok(id_, {"contents": [{"uri": uri, "text": ctx or "(no domain context)"}]})
        return _err(id_, -32602, f"Unknown resource: {uri}")

    if method == "prompts/list":
        return _ok(id_, {"prompts": [{"name": "system", "description": "Agent system prompt"}]})

    if method == "prompts/get":
        name = params.get("name", "")
        if name == "system":
            from app.agents.addon_tool_agent import addon_agent_cls
            return _ok(id_, {
                "messages": [{"role": "user", "content": {"type": "text", "text": addon_agent_cls("gpu-monitor", "gpu_monitoring")().get_system_prompt()}}]
            })
        return _err(id_, -32602, f"Unknown prompt: {name}")

    return _err(id_, -32601, f"Method not found: {method}")
