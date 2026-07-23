"""coresight-g — settings (env-driven)."""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

_env_file = f".env.{os.getenv('ENV', 'local')}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_env_file, extra="ignore")

    app_name: str = "coresight-g"  # [CUSTOMIZE]
    env: str = "local"

    # Database
    database_url: str = "sqlite:///./local.db"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Prometheus (관측 데이터 계층 — GPU/HW 메트릭·알람 조회)
    prometheus_url: str = "http://localhost:9090"

    # Loki (로그 수집·검색 — PRD P1)
    loki_url: str = "http://localhost:3100"

    # OpenTelemetry 트레이스 (PRD P1 — 자체 수집 파이프라인 관측)
    otel_enabled: bool = False
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    otel_service_name: str = "coresight-g-api"
    jaeger_url: str = "http://localhost:16686"  # 조회 API (trace-monitor addon 사용)

    # Alertmanager webhook 수신 (PRD P0 알림 채널)
    alert_webhook_token: str = "coresight-webhook-token"  # deploy/alertmanager/alertmanager.yml 과 일치
    notify_webhook_url: str = ""  # 설정 시 수신 알람을 외부 채널(webhook)로 중계

    # Auth
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Claude API (Orchestrator + Domain Agents)
    anthropic_api_key: str = ""
    orchestrator_model: str = "claude-sonnet-4-6"
    domain_agent_model: str = "claude-haiku-4-5-20251001"

    # OpenAI (선택)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Google Gemini (선택)
    google_api_key: str = ""
    google_model: str = "gemini-1.5-flash"

    # Ollama (로컬 LLM 폴백)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # CORS
    cors_origins: list[str] = ["http://localhost:4100"]

    # Setup Wizard
    setup_completed: bool = False

    # Default admin (첫 구동 시 시드) — 미설정 시 생성 안 함
    default_admin_user_id: str | None = None
    default_admin_password: str | None = None

    # MCP URL 외부 노출 호스트 (Docker/NAT 환경에서 host IP 명시)
    mcp_host: str = ""

    # Standalone Agent (F12)
    agent_standalone: bool = False
    agent_key: str = ""
    agent_port: int = 8001
    agent_base_url: str = "http://localhost:8001"
    agent_expose_protocol: str = ""  # "a2a,mcp" or ""


settings = Settings()
