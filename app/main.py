"""coresight-g — FastAPI entrypoint.

참조: SmartHaccp-MultiAgent app/main.py
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

# [CUSTOMIZE] 도메인 라우터 추가 시 여기에 import
from app.routers import (
    router_auth,
    router_users,
    router_agent,
    router_addon_agent,
    router_settings,
    router_setup,
    router_agent_config,
    router_agent_registry,
    router_a2a,
    router_mcp,
    router_mcp_config,
    router_metrics,
    router_alerts,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: DB 마이그레이션 → 컬럼 마이그레이션 → 기본 관리자 시드 → Addon 로더 초기화
    from app.db import apply_column_migrations, run_migrations, seed_default_admin
    from app.addon_agent_loader import init as addon_init

    await run_migrations()
    await apply_column_migrations()
    await seed_default_admin()
    await addon_init(app)
    from app.services import mcp_proxy_server
    await mcp_proxy_server.init_from_db()
    yield
    # shutdown


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

# OTel 계측 (OTEL_ENABLED=true 시) — 미들웨어 추가라 앱 기동 전 호출 필수
from app.core.tracing import setup_tracing  # noqa: E402

setup_tracing(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def addon_guard(request: Request, call_next):
    """비활성 addon API 요청 차단."""
    path = request.url.path
    if path.startswith("/api/addon/"):
        from app.addon_agent_loader import is_active_prefix
        if not is_active_prefix(path):
            return JSONResponse({"detail": "비활성화된 에이전트입니다."}, status_code=404)
    return await call_next(request)

app.include_router(router_auth.router)
app.include_router(router_users.router)
app.include_router(router_agent.router)
app.include_router(router_addon_agent.router)
app.include_router(router_settings.router)
app.include_router(router_setup.router)
app.include_router(router_agent_config.router)
app.include_router(router_agent_registry.router)
app.include_router(router_a2a.router)        # A2A Protocol v1.0 (F12)
app.include_router(router_mcp.router)        # MCP JSON-RPC 2.0 (F12)
app.include_router(router_mcp_config.router) # MCP Proxy 설정 관리 (F12)
app.include_router(router_metrics.router)    # GPU/HW 메트릭·알람 조회 (PRD P0)
app.include_router(router_alerts.router)     # Alertmanager webhook 수신·이력 (PRD P0)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "env": settings.env,
        "mode": "standalone" if settings.agent_standalone else "embedded",
    }
