# CoreSight-G Platform

> **[한국어 →](README.md)** · **wise-dev-standard / python-fastapi × ict-saas**  
> Unified observability platform for on-prem GPU servers + hardware — Multi AI Agent architecture (Orchestrator + AI Assistant)  
> [PRD](.docs/CoreSightG-PRD.md) · [COMPLIANCE.md](COMPLIANCE.md)

## Overview

A full-observability platform (metrics · logs · traces · alerts) that unifies on-prem GPU servers (1–20 nodes)
and server hardware (CPU/RAID/sensors/BMC) into a single monitoring system. GPU telemetry
(utilization/VRAM/ECC/XID) and hardware health are correlated in one dashboard, with a natural-language
monitoring assistant powered by a Multi AI Agent architecture (Orchestrator + Domain Agents).
Based on `Wise-MultiAIAgent-Template`.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI · Python 3.12 · uv · SQLAlchemy 2 · Alembic |
| Frontend | Vite + React 19 · TypeScript · Tailwind CSS v4 · react-router v7 |
| DB | SQLite (local) / PostgreSQL 17 (dev+) + Redis 7.4 |
| LLM | Anthropic Claude (primary) · Ollama (local fallback) |
| Observability | Prometheus v3.9 (scrape 15s · retention 15d) · 7 alert rules · mock GPU exporter (local) |
| Deploy | Docker Compose → Kubernetes + Helm |

## Prerequisites (Pre-install)

| Item | Version | Install | Purpose |
|------|---------|---------|---------|
| Python | 3.12+ | python.org, or managed by uv | Backend |
| [uv](https://docs.astral.sh/uv/) | latest | `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Python packages/venv |
| Node.js | 20+ | nodejs.org / nvm | Frontend |
| pnpm | 11+ | `npm i -g pnpm` (or `corepack enable`) | Frontend packages |
| pm2 | 7+ | `npm i -g pm2` | local-mode process manager (`make local-all`) |
| Docker Desktop | latest | docker.com | All infra containers |

### Observability stack (Prometheus · Alertmanager · mock exporter) — no manual install

`make up` pulls and starts the images via docker compose automatically.

| Service | Image | Port | Config |
|---------|-------|------|--------|
| prometheus | `prom/prometheus:v3.9.1` | 9090 | `deploy/prometheus/prometheus.yml` (scrape 15s, retention 15d) |
| alertmanager | `prom/alertmanager:v0.28.1` | 9093 | `deploy/alertmanager/alertmanager.yml` (webhook → backend) |
| gpu-mock-exporter | `python:3.12-alpine` | 9400 | `scripts/mock_gpu_exporter.py` (local dev, simulates 4 GPUs) |
| loki | `grafana/loki:3.4.2` | 3100 | `deploy/loki/loki-config.yml` (log store/search, retention 15d) |
| log-generator | `python:3.12-alpine` | — | `scripts/mock_log_generator.py` (local dev syslog/dmesg/BMC logs) |
| jaeger | `jaegertracing/all-in-one:1.62.0` | 16686 UI / 4318 OTLP | Trace collection/query. Instrumentation: `OTEL_ENABLED=true` (`app/core/tracing.py`) |

- **Webhook token**: `credentials` in `deploy/alertmanager/alertmanager.yml` must match
  `ALERT_WEBHOOK_TOKEN` in `.env.*` (default `coresight-webhook-token`; change in production).
- **local mode**: Alertmanager container reaches the host pm2 backend via `host.docker.internal`
  (`extra_hosts` already set). For dev+ (api in Docker), switch the url to `http://api:8000/api/alerts/webhook`.
- **Anomaly scenario**: `MOCK_ANOMALY=1 docker compose --env-file .env.local up -d --force-recreate gpu-mock-exporter`
  → fires GPU3 overheat/XID/ECC/RAID alerts.
- **Production**: remove `gpu-mock-exporter` and register real DCGM Exporter (9400) /
  node_exporter / ipmi_exporter as scrape targets in `deploy/prometheus/prometheus.yml`.

### LLM (monitoring assistant)

| Option | Setup | Notes |
|--------|-------|-------|
| Claude (recommended) | Set `ANTHROPIC_API_KEY` in `.env.local` | Full intent classification + tool_use loop |
| Ollama (fallback) | `make up` (container) or native + `ollama pull llama3.2` | Auto-fallback without API key — no tool_use, text/`<api_call>` responses |

## Quick Start

```bash
# 1. Create new repo from template, then clone
git clone https://github.com/your-org/your-project.git
cd your-project

# 2. Set environment variables
cp .env.example .env.local
# Edit .env.local: set ANTHROPIC_API_KEY

# 3. Install dependencies
uv sync
cd front && pnpm install && cd ..

# 4a. Local all-in-one (pm2 required: npm i -g pm2)
make local-all   # Ollama Docker + BE/FE via pm2 (SQLite auto)
make local-logs  # monitor logs

# 4b. Separate terminals (no pm2 needed)
make up      # infra (postgres + redis + ollama)
make dev-be  # Terminal 1 → http://localhost:8100
make dev-fe  # Terminal 2 → http://localhost:4100

# 5. Open Setup Wizard
open http://localhost:4100
```

## Environment Modes

| Mode | Command | DB | Runtime |
|------|---------|-----|---------|
| **local** | `make local-all` | SQLite | Ollama Docker + BE/FE pm2 |
| **dev** | `make dev-all` | PostgreSQL | Docker Compose |
| **staging** | `make staging-all` | PostgreSQL | Docker Compose |
| **prod** | `make prod-all` | PostgreSQL (HA) | Docker Compose |

### Log Monitoring

| Mode | Command | Backend |
|------|---------|---------|
| local | `make local-logs` | pm2 logs (non-Docker) |
| local | `make local-status` | pm2 status |
| dev | `make dev-logs` | docker compose logs -f |
| staging | `make staging-logs` | docker compose logs -f |
| prod | `make prod-logs` | docker compose logs -f api |

## Endpoints

| URL | Description |
|-----|-------------|
| `http://localhost:8100/health` | Health check |
| `http://localhost:8100/docs` | Swagger UI |
| `http://localhost:8100/redoc` | ReDoc |
| `http://localhost:4100` | React frontend (dev) |
| `http://localhost:11434` | Ollama API |
| `http://localhost:9090` | Prometheus (metrics TSDB · alert rules) |
| `http://localhost:9093` | Alertmanager (alert routing → backend webhook) |
| `http://localhost:9400/metrics` | mock GPU/HW exporter (local dev) |
| `http://localhost:3100` | Loki (log store/search) |
| `http://localhost:16686` | Jaeger UI (OTel traces) |

## API Examples

```bash
TOKEN=$(curl -s -X POST http://localhost:8100/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id":"admin","password":"Admin123!"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# SSE streaming chat
curl -X POST http://localhost:8100/api/agent/chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"Hello","history":[]}'

# Create user (supervisor/admin only)
curl -X POST http://localhost:8100/api/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"alice","username":"Alice","password":"Secure123!","role":"user"}'

# Setup Wizard status
curl http://localhost:8100/api/setup/status

# Toggle agent activation (admin+)
curl -X PATCH http://localhost:8100/api/agent-config/example \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_enabled": false}'

# Upload Addon Agent ZIP (admin+)
curl -X POST "http://localhost:8100/api/addon-agents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@MyAddon.zip"

# Get settings (API keys masked)
curl http://localhost:8100/api/settings/ -H "Authorization: Bearer $TOKEN"

# GPU metrics snapshot (utilization/VRAM/temperature/power/XID/ECC)
curl http://localhost:8100/api/metrics/gpu -H "Authorization: Bearer $TOKEN"
# → {"gpus":[{"hostname":"gpu-node-01","gpu":"0","util_percent":87.9,"vram_used_percent":82.3,...}]}

# Server hardware snapshot (CPU/memory/RAID/PSU/temperature)
curl http://localhost:8100/api/metrics/hardware -H "Authorization: Bearer $TOKEN"

# Active alerts
curl http://localhost:8100/api/metrics/alerts -H "Authorization: Bearer $TOKEN"

# Monitoring addon agent tools (implementations: addon-agents/zip/)
curl http://localhost:8100/api/addon/gpu-monitor/tools -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/gpu-monitor/tools/get_gpu_snapshot \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
curl http://localhost:8100/api/addon/hw-monitor/status -H "Authorization: Bearer $TOKEN"
# → {"node_count":1,"faulty":0,"healthy":1}

# GPU utilization time series (dashboard sparklines)
curl "http://localhost:8100/api/metrics/gpu/history?minutes=30&step=60" -H "Authorization: Bearer $TOKEN"

# Log search — Addon-first: via log-analyzer addon (no core /api/logs)
curl -X POST http://localhost:8100/api/addon/log-analyzer/tools/search_logs \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"job":"dmesg","keyword":"Xid","minutes":60}'
curl http://localhost:8100/api/addon/log-analyzer/status -H "Authorization: Bearer $TOKEN"
# → {"error_count_1h":0}

# Workload correlation — workload-correlator addon (P2-7, GPU process↔job/user)
curl -X POST http://localhost:8100/api/addon/workload-correlator/tools/get_usage_by_job \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'

# Network monitoring — net-monitor addon (P2-6)
curl -X POST http://localhost:8100/api/addon/net-monitor/tools/get_nic_snapshot \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'

# Anomaly detection — anomaly-detector addon (P2-5)
curl -X POST http://localhost:8100/api/addon/anomaly-detector/tools/detect_metric_anomalies \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"promql":"DCGM_FI_DEV_GPU_TEMP","hours":6}'
curl -X POST http://localhost:8100/api/addon/anomaly-detector/tools/correlate_alerts \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'

# Capacity planning/efficiency — capacity-planner addon (P2-4)
curl -X POST http://localhost:8100/api/addon/capacity-planner/tools/get_efficiency_report \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"hours":24}'
curl -X POST http://localhost:8100/api/addon/capacity-planner/tools/get_underutilized_gpus \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"hours":24,"threshold_percent":10}'

# GPU profiling — gpu-profiler addon (P2-3, SM/Tensor/DRAM/throttle)
curl -X POST http://localhost:8100/api/addon/gpu-profiler/tools/get_gpu_profile \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'

# BMC/IPMI query — bmc-monitor addon (P2-2, Prometheus+Loki combined)
curl -X POST http://localhost:8100/api/addon/bmc-monitor/tools/get_bmc_sensors \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
curl -X POST http://localhost:8100/api/addon/bmc-monitor/tools/get_bmc_events \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"level":"error","minutes":120}'

# Storage diagnostics — storage-monitor addon (P2-1)
curl -X POST http://localhost:8100/api/addon/storage-monitor/tools/get_storage_snapshot \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
# → {"devices":[{"device":"nvme0n1","read_latency_ms":2.15,"iops_read":8838,...}],"raid":[...]}

# Trace query — trace-monitor addon
curl -X POST http://localhost:8100/api/addon/trace-monitor/tools/search_traces \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"service":"coresight-g-api","minutes":30}'

# Alert history (stored via Alertmanager → webhook)
curl "http://localhost:8100/api/alerts/history?limit=20" -H "Authorization: Bearer $TOKEN"
# → {"alerts":[{"alertname":"GPUXidError","severity":"critical","hostname":"gpu-node-01","gpu":"3","status":"firing",...}]}

# Direct PromQL query
curl -G http://localhost:8100/api/metrics/query --data-urlencode 'q=DCGM_FI_DEV_GPU_TEMP > 80' \
  -H "Authorization: Bearer $TOKEN"

# Logout (token blacklist)
curl -X POST http://localhost:8100/api/auth/logout -H "Authorization: Bearer $TOKEN"
```

## RBAC Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `supervisor` | Super admin | Full access (including user deletion) |
| `admin` | Admin | Create users, modify settings |
| `user` | Regular user | Chat, read |
| `viewer` | Read-only | Read only |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `passlib + bcrypt ValueError` | bcrypt 4.x incompatible with passlib | Using `bcrypt>=4.0` directly (already applied) |
| `ERR_PNPM_IGNORED_BUILDS` | pnpm v10 dropped `package.json` pnpm field | Using `front/pnpm-workspace.yaml` (already applied) |
| `port 8100 already in use` | Stale uvicorn process | `pkill -f "uvicorn app.main"` |
| Ollama connection failed | `make up` not run | Run `make up`, then `curl http://localhost:11434/api/tags` |
| Docker MCP URL returns internal IP (172.x.x.x) | Container IP auto-detection limitation | Set `MCP_HOST=<host IP>` in `.env.dev` / `.env.prod` |
| Docker `/mcp` returns 404 | nginx missing `/mcp` location | Add `/mcp` location to `front/nginx.conf` (already applied) |
| PostgreSQL `initdb.d` SQL error (`AUTOINCREMENT`) | SQLite-dialect SQL applied to PostgreSQL | `sql/pg/` split + `docker-compose.yml` mount fixed (already applied) |
| pm2 `Failed to spawn: uvicorn` | `.venv` shebang paths broken after project directory rename | `rm -rf .venv && uv sync`, then `pm2 restart` |
| `/health` returns `"env":"[object Object]"` | pm2 daemon/local version mismatch injects lowercase `env` | `pm2 update` |
| `/api/metrics/*` returns 503 | Prometheus not running | `make up` (includes prometheus + gpu-mock-exporter) |
| UI-less addon shows up in sidebar | Menu filter only checked `is_active` | `has_front` filter added (already applied) — API-only addons are hidden |
| Chat "agent list" omits ADDON agents | Formatter only queried `tbl_agent_config` (built-in only) | Merged `tbl_addon_agents` (already applied) — shows built-in/monitoring/ADDON groups |
| Addon re-upload creates a duplicate raw-key entry under monitoring agents | `_VALID_TYPES` missed `"monitoring"` → agent_type silently reset to "app", bypassing the Addon-first guard | Added `"monitoring"` to `_VALID_TYPES` (already applied) |

## Customization

1. Monitoring agent implementations live in `addon-agents/zip/<agent>/`, not in core —
   `<agent>-app.py` exports `router` + `_TOOLS` + `TOOL_EXECUTORS` + `SYSTEM_PROMPT` (contract)
   - **Dashboard widget contract**: if an addon implements `GET /status`, it appears automatically
     as an "Agent Widgets" card when enabled (top-level number/string fields). Addons without it are skipped silently
2. Update `app/agents/orchestrator.py`: `_VALID_INTENTS`, `_AGENT_MAP` (`addon_agent_cls("<agent>", "<intent>")`), `_CLASSIFY_SYSTEM`
3. Add domain tables to `sql/sqlite/01_init.sql` **and** `sql/pg/01_init.sql` (keep both in sync)
4. Add domain pages to `front/src/App.tsx`

See [`.docs/guides/02-development.md`](.docs/guides/02-development.md) for details.

## Frontend Pages

| Route | Description | Auth |
|-------|-------------|------|
| `/setup` | Setup Wizard (Supervisor → **TOTP 2FA** → LLM settings) | None |
| `/login` | Login (TOTP 2-step auth supported) | None |
| `/dashboard` | Unified monitoring dashboard (active alerts + GPU cards/sparklines + HW node table, 15s polling, default route) | Login |
| `/chat` | AI Assistant (sessions, model selector, SSE streaming) | Login |
| `/agents` | Agent management (toggle, Addon ZIP upload, MCP status · guide · config edit · delete) | admin+ |
| `/users` | User management (CRUD) | admin+ |
| `/settings` | System settings (LLM connection test) | admin+ |
| `/profile` | My Page (profile · password · **TOTP 2FA** management) | Login |

## Implementation Status

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Auth (F5) · User management · Settings (F9) | ✅ PASS (test/impl/1) |
| 2 | Login UI · Chat UI · SSE streaming (F7) | ✅ PASS (test/impl/2) |
| 3 | Setup Wizard API (F6) · Agent Config (F8) · Addon Agent ZIP (F4) | ✅ PASS (test/impl/3) |
| 4 | Setup Wizard UI · AppLayout · Agents/Users/Settings management pages | ✅ PASS (test/impl/4) |
| 5 | F12 — A2A Protocol v1.0 · MCP JSON-RPC 2.0 · Agent Registry | ✅ PASS (test/impl/5) |
| 6 | F13~F16 — TOTP · Theme · My Page · Settings UI · Addon toggle · Required agent badge | ✅ Done |
| 7 | F17~F19 — AI hallucination prevention · Custom instructions (system/user) · i18n (ko/en) | ✅ Done |
| 8 | F20~F21 + F12 redesign — Keyword ruleset · Addon API guard · MCP Proxy per-agent · MCP status (green/orange/red) · MCP config CRUD · MCP guide/edit/delete UI | ✅ PASS (test/impl/6) |
| 9 (v2) | F22 Agent Catalog — 9 agent types · `-meta.json` standard · catalog API · scaffold API · 4 templates (Board/Service/ToolProxy/RAG) · BUG-v1.4-01 sql_path fix | ✅ PASS (test/impl/8) |
| 10 (v2) | F23 Registry v2 — capability-based search · Agent Card · heartbeat/lease · lifecycle_state · tbl_addon_agent_capabilities · auto-save capabilities on upload | ✅ PASS (test/impl/9) |
| 11 (v2) | F24 Agent Builder UI — 4-step Wizard · 9-type card selection · scaffold ZIP download/deploy · domain substitution bug fix | ✅ PASS (test/impl/10) |
| 12 (v2) | F25 Orchestrator Enhancement — capability-based Registry routing · Reviewer Gate · HITL Gate · SSE events (registry_miss/hitl_pending/review_gate) · opt-in settings | ✅ PASS (test/impl/11) |
| 13 (v2) | UI Merge — unified "New Agent" modal with tabs (scaffolding / ZIP upload) · .omc system file filter | ✅ PASS (test/impl/12) |
| 14 (v2) | LLM settings priority bug fix — .env.* values take precedence over DB (os.environ > .env > DB > default) | ✅ PASS (test/impl/13) |

## Implemented Endpoints

| Path | Method | Description | Auth |
|------|--------|-------------|------|
| `/health` | GET | Health check | None |
| `/api/auth/login` | POST | Login → JWT (TOTP supported) | None |
| `/api/auth/logout` | POST | Logout (blacklist) | Bearer |
| `/api/auth/me` | GET | Get own profile | Bearer |
| `/api/auth/me` | PATCH | Update profile / password | Bearer |
| `/api/auth/totp/qr` | GET | Issue TOTP QR URI | Bearer |
| `/api/auth/totp/enable` | POST | Enable TOTP (verify code) | Bearer |
| `/api/auth/totp/disable` | POST | Disable TOTP (verify code) | Bearer |
| `/api/users/` | GET/POST | List/create users | admin+ |
| `/api/users/{id}` | DELETE | Delete user | supervisor |
| `/api/agent/chat` | POST | Non-streaming chat | Bearer |
| `/api/agent/chat/stream` | POST | SSE streaming chat | Bearer |
| `/api/settings/` | GET | Get settings (masked) | Bearer |
| `/api/settings/{key}` | PUT | Update setting | admin+ |
| `/api/settings/test-llm` | POST | LLM connection test | Bearer |
| `/api/setup/status` | GET | Setup Wizard status | None |
| `/api/setup/supervisor` | POST | Create first supervisor | None |
| `/api/setup/llm-provider` | PUT | Save LLM settings | None |
| `/api/setup/complete` | POST | Mark setup done | None |
| `/api/agent-config/` | GET | List agent configs | Bearer |
| `/api/agent-config/{key}` | GET/PATCH | Get/update agent config | Bearer/admin+ |
| `/api/addon-agents/` | GET | List addons | Bearer |
| `/api/addon-agents/upload` | POST | Upload ZIP + hot deploy | admin+ |
| `/api/addon-agents/{key}` | DELETE | Delete addon | admin+ |
| `/api/addon-agents/{key}` | PATCH | Rename addon | admin+ |
| `/api/addon-agents/{key}/toggle` | PATCH | Toggle addon active/inactive | admin+ |
| `/api/addon-agents/templates/list` | GET | List templates (with agent_type) | Bearer |
| `/api/addon-agents/templates/download/{name}` | GET | Download template ZIP | Bearer |
| `/api/addon-agents/catalog` | GET | Agent catalog (grouped by type) | Bearer |
| `/api/addon-agents/scaffold` | POST | Generate scaffolding ZIP | Bearer |
| `/api/addon-agents/guide` | GET | Addon dev guide (README.md) | Bearer |
| `/api/addon/{key}/*` | ANY | Dynamic addon routes (active only) | Bearer |
| `/mcp` | POST | MCP JSON-RPC 2.0 (global) | Bearer |
| `/mcp/guide` | GET | MCP guide + client config snippets | None |
| `/mcp/{agent_key}` | POST | MCP JSON-RPC 2.0 (per-agent) | Bearer |
| `/mcp/{agent_key}/guide` | GET | Per-agent MCP guide | None |
| `/api/mcp-configs/` | GET | List MCP configs | Bearer |
| `/api/mcp-configs/{key}` | GET | Get MCP config | Bearer |
| `/api/mcp-configs/{key}` | PUT | Register/update MCP config (upsert) | admin+ |
| `/api/mcp-configs/{key}` | DELETE | Remove MCP mapping (agent stays active) | admin+ |
| `/api/mcp-configs/{key}/status` | GET | MCP status (green/orange/red) | Bearer |
| `/api/agent-registry/` | GET/POST | List / register external agents | admin+ |
| `/api/agent-registry/{key}` | DELETE | Deregister external agent | admin+ |
| `/api/agent-registry/{key}/ping` | POST | Ping connectivity test | admin+ |
| `/api/agent-registry/search` | POST | capability/verb/domain/type search | admin+ |
| `/api/agent-registry/{key}/card` | GET | Agent Card (auto-generated or stored) | admin+ |
| `/api/agent-registry/{key}/card` | PUT | Update Agent Card JSON directly | admin+ |
| `/api/agent-registry/{key}/heartbeat` | POST | Heartbeat refresh + lease extend | admin+ |
| `/api/agent-registry/{key}/health` | GET | Live health status (health_dot, lease_expired) | admin+ |

## Addon Agent Catalog (v2)

9 agent types can be packaged as ZIP and registered/extended.

| Type | Template | Role |
|------|----------|------|
| `app` | Board | Full-stack app with FE+BE+DB (e.g., boards) |
| `service` | ServiceAgent | Backend business logic only |
| `tool-proxy` | ToolProxyAgent | External REST API → MCP adapter |
| `rag` | RagAgent | Document embedding + vector search Q&A |
| `reviewer` | — | Quality gate / hallucination detection (template TBD) |
| `execution` | — | Code execution / batch jobs (template TBD) |
| `hitl` | — | Human-in-the-loop approval gateway (template TBD) |
| `memory` | — | Long-term state / user preference store (template TBD) |
| `federation` | — | External A2A/MCP agent gateway (template TBD) |

### `-meta.json` standard

Include `{AgentName}-meta.json` in the ZIP for automatic type recognition:

```json
{
  "agent_type": "service",
  "version": "1.0.0",
  "description": "Processes business logic and returns results",
  "capabilities": [
    {
      "verb": "process",
      "domain": "service.my-domain",
      "description": "Process input and return output"
    }
  ],
  "governance": {"data_classification": "internal"},
  "required_env": [],
  "optional_env": ["ANTHROPIC_API_KEY"]
}
```

Without `-meta.json`, `agent_type` defaults to `"app"` (v1.4 backward compatible).

### Scaffolding

```bash
# Generate a new Service Agent scaffold ZIP
curl -X POST http://localhost:8100/api/addon-agents/scaffold \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_name":"MyAnalytics","agent_type":"service","description":"Data analysis"}' \
  -o MyAnalytics.zip

# Upload immediately
curl -X POST "http://localhost:8100/api/addon-agents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@MyAnalytics.zip"

# Browse catalog (grouped by type)
curl http://localhost:8100/api/addon-agents/catalog \
  -H "Authorization: Bearer $TOKEN"

# Filter by type
curl "http://localhost:8100/api/addon-agents/catalog?agent_type=service" \
  -H "Authorization: Bearer $TOKEN"
```

## Agent Registry v2 (F23)

Register external standalone agents and discover them by capability.

### Register an External Agent

```bash
curl -X POST http://localhost:8100/api/agent-registry/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_key": "hr-rag-agent",
    "agent_name": "HR Knowledge Agent",
    "agent_type": "rag",
    "agent_card_url": "http://hr-agent:9001/.well-known/agent-card.json",
    "capabilities_json": "[{\"verb\":\"retrieve\",\"domain\":\"knowledge.hr\"}]"
  }'
```

### Capability-Based Search

```bash
# Search by verb
curl -X POST http://localhost:8100/api/agent-registry/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"capabilities": ["retrieve"], "lifecycle_state": "active"}'

# Filter by domain prefix + agent_type
curl -X POST http://localhost:8100/api/agent-registry/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain_prefix": "knowledge.", "agent_type": "rag"}'
```

### Agent Card · Heartbeat · Health

```bash
# Get Agent Card (auto-generated if not stored)
curl http://localhost:8100/api/agent-registry/hr-rag-agent/card \
  -H "Authorization: Bearer $TOKEN"

# Heartbeat (extends lease 30 min, recovers quarantined → active)
curl -X POST http://localhost:8100/api/agent-registry/hr-rag-agent/heartbeat \
  -H "Authorization: Bearer $TOKEN"

# Health status (health_dot: green/orange/red)
curl http://localhost:8100/api/agent-registry/hr-rag-agent/health \
  -H "Authorization: Bearer $TOKEN"
```

### lifecycle_state

| State | Description | health_dot |
|-------|-------------|-----------|
| `active` | Normal operation | green |
| `quarantined` | Fault / isolated (heartbeat restores) | red |
| `retired` | Decommissioned | red |
| `draft` | Registration in progress | orange |

## Developer Guides

| Guide | Audience |
|-------|----------|
| [G1: Getting Started](.docs/guides/01-getting-started.md) | New users |
| [G2: Development](.docs/guides/02-development.md) | Developers |
| [G3: Testing](.docs/guides/03-testing.md) | Developers·QA |
| [G4: Deployment](.docs/guides/04-deployment.md) | DevOps |
| [G5: Operations](.docs/guides/05-operations.md) | Admins |
| [G6: Standalone A2A/MCP](.docs/guides/06-standalone.md) | Developers·DevOps |

## MCP Proxy

All non-required agents (builtin toggleable + Addon) are exposed as independent MCP servers when activated.

```bash
# Register MCP config (port + custom args)
curl -X PUT http://localhost:8100/api/mcp-configs/{agent_key} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"port": 20001, "extra_args": ["--header:x-api-key:token"]}'

# Check MCP status (green/orange/red)
curl http://localhost:8100/api/mcp-configs/{agent_key}/status \
  -H "Authorization: Bearer $TOKEN"

# Per-agent MCP guide (status, tool list, client config snippets)
curl http://localhost:8100/mcp/{agent_key}/guide

# MCP → list tools
curl -X POST http://localhost:8100/mcp/{agent_key} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

**Claude Desktop integration (mcp-remote bridge):**

```json
{
  "mcpServers": {
    "{agent_key}": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8100/mcp/{agent_key}"]
    }
  }
}
```

**Agent management UI (`/agents`):**

All active non-required agents (builtin toggle + Addon) show MCP sub-features:
- `●` — MCP status dot: 🟢 green (port set + agent active) · 🟠 orange (loading) · 🔴 red (port not set/error) — polls every 4s
- `ⓘ` — MCP guide modal: URL, status banner, tool list, Claude Desktop/Cursor/VSCode config + copy buttons
- `✎` — MCP config edit: port (optional) + custom args (key:value rows, add/delete)
- `✕` — Remove MCP mapping (agent stays active, MCP not provided)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | — | Claude API Key (required) |
| `ORCHESTRATOR_MODEL` | `claude-sonnet-4-6` | Orchestrator LLM |
| `DOMAIN_AGENT_MODEL` | `claude-haiku-4-5-20251001` | Domain Agent LLM |
| `OLLAMA_MODEL` | `llama3.2` | Ollama fallback model |
| `JWT_SECRET_KEY` | `change-me` | JWT signing key (change in production) |
| `MCP_HOST` | _(auto)_ | MCP URL host IP/domain (required in Docker environments) |

See `.env.example` for full list.

## Next Steps (Remaining PRD)

- Alembic migrations for PostgreSQL
- Redis JWT blacklist (currently in-memory)
- GitHub Actions CI pipeline completion

## References

- [PRD](.docs/Multi%20AI%20Agent%20Standard-PRD.md)
- [Architecture Guide](Multi%20AI%20Agent%20아키텍처%20가이드%20v1.0.md)
- [Getting Started](.docs/guides/01-getting-started.md)
