-- coresight-g — DB 스키마 초기화 (idempotent, SQLite)

CREATE TABLE IF NOT EXISTS tbl_users (
    serial       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      VARCHAR(50)  NOT NULL UNIQUE,
    username     VARCHAR(50),
    email        VARCHAR(100),
    password     VARCHAR(200) NOT NULL,
    role         VARCHAR(20)  NOT NULL DEFAULT 'user',
    status       VARCHAR(20)  NOT NULL DEFAULT 'active',
    custom_instructions TEXT,
    totp_secret  TEXT,
    totp_enabled INTEGER      NOT NULL DEFAULT 0,
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP
);

-- Agent 활성화 설정 (F8)
CREATE TABLE IF NOT EXISTS tbl_agent_config (
    agent_key    VARCHAR(50)  PRIMARY KEY,
    agent_name   VARCHAR(100) NOT NULL,
    is_enabled   INTEGER      NOT NULL DEFAULT 1,
    is_required  INTEGER      NOT NULL DEFAULT 0,
    model        TEXT,
    system_prompt TEXT,
    nav_group    VARCHAR(50),
    sort_order   INTEGER      NOT NULL DEFAULT 0,
    updated_at   TIMESTAMP
);

-- Addon Agent 등록 (F4 + F22)
CREATE TABLE IF NOT EXISTS tbl_addon_agents (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_key    VARCHAR(50)  NOT NULL UNIQUE,
    agent_name   VARCHAR(100) NOT NULL,
    router_path  VARCHAR(500),
    api_prefix   VARCHAR(100) NOT NULL,
    sql_path     VARCHAR(500),
    has_app      INTEGER      NOT NULL DEFAULT 0,
    has_front    INTEGER      NOT NULL DEFAULT 0,
    agent_type   TEXT         NOT NULL DEFAULT 'app',
    meta_json    TEXT,
    is_builtin   INTEGER      NOT NULL DEFAULT 0,
    is_active    INTEGER      NOT NULL DEFAULT 1,
    uploaded_by  VARCHAR(50),
    uploaded_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 시스템 설정 (F9, key-value)
CREATE TABLE IF NOT EXISTS tbl_settings (
    key          VARCHAR(100) PRIMARY KEY,
    value        TEXT,
    description  VARCHAR(200),
    updated_at   TIMESTAMP
);

-- Agent Registry — 외부 Standalone Agent (F12 + F23)
CREATE TABLE IF NOT EXISTS tbl_agent_registry (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_key          VARCHAR(50)  NOT NULL UNIQUE,
    agent_name         VARCHAR(100) NOT NULL,
    protocol           VARCHAR(10)  NOT NULL DEFAULT 'a2a',
    agent_card_url     VARCHAR(500),
    mcp_endpoint       VARCHAR(500),
    auth_token         TEXT,
    agent_type         TEXT         NOT NULL DEFAULT 'service',
    capabilities_json  TEXT,
    agent_card_json    TEXT,
    lifecycle_state    TEXT         NOT NULL DEFAULT 'active',
    health_score       REAL         NOT NULL DEFAULT 1.0,
    last_heartbeat_at  TIMESTAMP,
    lease_expires_at   TIMESTAMP,
    is_active          INTEGER      NOT NULL DEFAULT 1,
    last_seen_at       TIMESTAMP,
    created_by         VARCHAR(50),
    created_at         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Addon Agent Capability 인덱스 (F23)
CREATE TABLE IF NOT EXISTS tbl_addon_agent_capabilities (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_key      VARCHAR(50)  NOT NULL,
    capability_key VARCHAR(100) NOT NULL,
    verb           VARCHAR(50)  NOT NULL,
    domain         VARCHAR(200) NOT NULL,
    description    TEXT,
    input_schema   TEXT,
    output_schema  TEXT,
    qos_json       TEXT,
    created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_key, capability_key)
);

-- MCP Proxy 설정 (F12 MCP)
CREATE TABLE IF NOT EXISTS tbl_mcp_configs (
    agent_key    VARCHAR(50)  PRIMARY KEY,
    port         INTEGER,
    extra_args   TEXT,
    is_enabled   INTEGER      NOT NULL DEFAULT 1,
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP
);

-- 감사 로그
CREATE TABLE IF NOT EXISTS tbl_audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    VARCHAR(50),
    action     VARCHAR(100) NOT NULL,
    target     VARCHAR(200),
    detail     TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 알람 수신 이력 (Alertmanager webhook — PRD §3 P0 필수 알람 채널)
CREATE TABLE IF NOT EXISTS tbl_alert_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    alertname   VARCHAR(100) NOT NULL,
    severity    VARCHAR(20),
    layer       VARCHAR(30),
    hostname    VARCHAR(100),
    gpu         VARCHAR(10),
    status      VARCHAR(20)  NOT NULL,
    summary     TEXT,
    starts_at   VARCHAR(50),
    ends_at     VARCHAR(50),
    payload     TEXT,
    received_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
