# CoreSight-G Platform

> **[English →](README.en.md)** · **wise-dev-standard / python-fastapi × ict-saas**  
> 온프레미스 GPU 서버 + 하드웨어 통합 관측성 플랫폼 — Orchestrator + AI Assistant 이중 구조 Multi AI Agent 아키텍처  
> [PRD](.docs/CoreSightG-PRD.md) · [COMPLIANCE.md](COMPLIANCE.md)

## 개요

온프레미스 GPU 서버(1~20대)와 서버 하드웨어(CPU/RAID/센서/BMC)를 하나의 관제 체계로 묶는
풀 관측성(메트릭·로그·트레이스·알림) 플랫폼. GPU 메트릭(utilization/VRAM/ECC/XID)과
하드웨어 상태를 통합 대시보드에서 상관 조회하고, 자연어 관제 어시스턴트(Multi AI Agent)로 원인을 분석한다.
기반 골격: `Wise-MultiAIAgent-Template` (Orchestrator + Domain Agent 이중 구조).

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| Backend | FastAPI · Python 3.12 · uv · SQLAlchemy 2 · Alembic |
| Frontend | Vite + React 19 · TypeScript · Tailwind CSS v4 · react-router v7 |
| DB | SQLite (local) / PostgreSQL 17 (dev+) + Redis 7.4 |
| LLM | Anthropic Claude (primary) · Ollama (local fallback) |
| 관측 | Prometheus v3.9 (scrape 15s · retention 15d) · 알람 규칙 7종 · mock GPU exporter (로컬) |
| 배포 | Docker Compose → Kubernetes + Helm |

## 사전 요구사항 (Pre-install)

| 항목 | 버전 | 설치 | 용도 |
|------|------|------|------|
| Python | 3.12+ | python.org 또는 uv 가 자동 관리 | 백엔드 |
| [uv](https://docs.astral.sh/uv/) | 최신 | `pip install uv` 또는 `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Python 패키지/가상환경 |
| Node.js | 20+ | nodejs.org / nvm | 프론트엔드 |
| pnpm | 11+ | `npm i -g pnpm` (또는 `corepack enable`) | 프론트 패키지 |
| pm2 | 7+ | `npm i -g pm2` | local 모드 프로세스 관리 (`make local-all`) |
| Docker Desktop | 최신 | docker.com | 인프라 컨테이너 전체 |

### 관측 스택 (Prometheus·Alertmanager·mock exporter) — 별도 설치 불필요

`make up` 시 docker compose 가 이미지를 자동 pull·기동한다. 수동 설치 없음.

| 서비스 | 이미지 | 포트 | 설정 파일 |
|--------|--------|------|-----------|
| prometheus | `prom/prometheus:v3.9.1` | 9090 | `deploy/prometheus/prometheus.yml` (scrape 15s, retention 15d) |
| alertmanager | `prom/alertmanager:v0.28.1` | 9093 | `deploy/alertmanager/alertmanager.yml` (webhook → 백엔드) |
| gpu-mock-exporter | `python:3.12-alpine` | 9400 | `scripts/mock_gpu_exporter.py` (로컬 개발용 GPU 4장 시뮬레이션) |
| loki | `grafana/loki:3.4.2` | 3100 | `deploy/loki/loki-config.yml` (로그 저장·검색, retention 15d) |
| log-generator | `python:3.12-alpine` | — | `scripts/mock_log_generator.py` (로컬 개발용 syslog/dmesg/BMC 로그) |
| jaeger | `jaegertracing/all-in-one:1.62.0` | 16686 UI / 4318 OTLP | 트레이스 수집·조회. 계측: `OTEL_ENABLED=true` (`app/core/tracing.py`) |

- **알림 webhook 토큰**: `deploy/alertmanager/alertmanager.yml` 의 `credentials` 와 `.env.*` 의
  `ALERT_WEBHOOK_TOKEN` 이 일치해야 함 (기본 `coresight-webhook-token`, 운영 시 변경).
- **local 모드 주의**: Alertmanager 컨테이너 → 호스트 pm2 백엔드 전달은 `host.docker.internal` 사용
  (compose 에 `extra_hosts` 적용됨). dev+ (api 컨테이너) 는 url 을 `http://api:8000/api/alerts/webhook` 로 교체.
- **이상 시나리오 재현**: `MOCK_ANOMALY=1 docker compose --env-file .env.local up -d --force-recreate gpu-mock-exporter`
  → GPU3 과열·XID·ECC·RAID 알람 발화.
- **운영 전환**: `gpu-mock-exporter` 제거 후 실제 DCGM Exporter(9400)/node_exporter/ipmi_exporter 를
  `deploy/prometheus/prometheus.yml` scrape 대상으로 등록.

### LLM (관제 어시스턴트)

| 구분 | 설정 | 비고 |
|------|------|------|
| Claude (권장) | `.env.local` 에 `ANTHROPIC_API_KEY` 입력 | intent 분류·tool_use 루프 전체 동작 |
| Ollama (폴백) | `make up` 으로 컨테이너 기동 또는 네이티브 실행 + `ollama pull llama3.2` | API Key 없을 때 자동 폴백 — tool_use 미지원, 텍스트/`<api_call>` 응답 |

## 빠른 시작

```bash
# 1. 템플릿으로 새 저장소 생성 후 클론
git clone https://github.com/your-org/your-project.git
cd your-project

# 2. 환경변수 설정
cp .env.example .env.local
# .env.local 에서 ANTHROPIC_API_KEY 입력

# 3. 의존성 설치
uv sync
cd front && pnpm install && cd ..

# 4. 인프라 기동 (postgres + redis + ollama)
make up

# 5. 개발 서버 실행
make dev-be   # 터미널 1: Backend → http://localhost:8100
make dev-fe   # 터미널 2: Frontend → http://localhost:4100

# 6. Setup Wizard 접속
open http://localhost:4100
```

## 환경별 실행

| 환경 | 명령 | DB | 실행 방식 |
|------|------|-----|----------|
| **local** | `make local-all` | SQLite | Ollama Docker + BE/FE pm2 |
| **dev** | `make dev-all` | PostgreSQL | Docker Compose 전체 |
| **staging** | `make staging-all` | PostgreSQL | Docker Compose 전체 |
| **prod** | `make prod-all` | PostgreSQL (HA) | Docker Compose 전체 |

### 로그 모니터링

| 환경 | 명령 | 백엔드 |
|------|------|--------|
| local | `make local-logs` | pm2 logs (비Docker) |
| local | `make local-status` | pm2 status |
| dev | `make dev-logs` | docker compose logs -f |
| staging | `make staging-logs` | docker compose logs -f |
| prod | `make prod-logs` | docker compose logs -f api |

### local 모드 사전 조건

```bash
npm i -g pm2   # pm2 설치 (최초 1회)
```

pm2 없이 개발 서버를 별도 터미널로 실행:

```bash
make up       # 인프라 전체 기동
make dev-be   # 터미널 1
make dev-fe   # 터미널 2
```

## Make 타겟

| 명령 | 설명 |
|------|------|
| `make local-all` | local 전체 기동 (Ollama Docker + BE/FE pm2) |
| `make local-stop` | local 전체 중단 |
| `make local-logs` | pm2 로그 모니터링 |
| `make local-status` | pm2 프로세스 상태 |
| `make dev-all` | dev 전체 기동 (docker compose, `.env.dev`) |
| `make dev-logs` | dev Docker 로그 |
| `make dev-stop` | dev 중단 |
| `make staging-all` | staging 전체 기동 |
| `make staging-logs` | staging Docker 로그 |
| `make prod-all` | prod 전체 기동 |
| `make prod-logs` | prod Docker 로그 (api 서비스만) |
| `make up` | 인프라만 기동 (postgres + redis + ollama) |
| `make down` | 전체 컨테이너 정리 |
| `make dev-be` | 백엔드 직접 실행 (`uvicorn --reload`) |
| `make dev-fe` | 프론트엔드 직접 실행 (`pnpm dev`) |
| `make db-reset` | DB 데이터 삭제 + 스키마 재생성 (Setup Wizard 재시험용) |
| `make seed` | 기본 설정 + 테스트 계정 삽입 (supervisor:admin/Admin123!) |
| `make db-fresh` | db-reset + seed 연속 실행 |
| `make test` | pytest 실행 |
| `make lint` | ruff 검사 |
| `make build` | Docker 이미지 빌드 |
| `make deploy` | Helm 배포 |
| `make standalone AGENT=X` | Standalone Agent 패키징 |

## 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `ANTHROPIC_API_KEY` | — | Claude API Key (필수) |
| `ORCHESTRATOR_MODEL` | `claude-sonnet-4-6` | Orchestrator LLM |
| `DOMAIN_AGENT_MODEL` | `claude-haiku-4-5-20251001` | Domain Agent LLM |
| `OLLAMA_MODEL` | `llama3.2` | Ollama 폴백 모델 |
| `JWT_SECRET_KEY` | `change-me` | JWT 서명 키 (운영 시 변경 필수) |
| `MCP_HOST` | _(자동)_ | MCP URL 노출 호스트 IP/도메인 (Docker 환경 필수) |

전체 목록: `.env.example` 참조

## 디렉터리 구조

```
├── app/                   # FastAPI 백엔드
│   ├── agents/            # Orchestrator + BaseAgent + ExampleAgent [CUSTOMIZE]
│   ├── tools/             # Tool 실행 함수 [CUSTOMIZE]
│   ├── services/          # LLM fallback 등 공통 서비스
│   ├── routers/           # API 라우터
│   └── core/              # 설정·보안
├── front/                 # Vite + React 프론트엔드
├── addon-agents/          # Addon Agent ZIP 패키지
│   ├── zip/               # 관제 Agent 구현체 11종 (내장 2: gpu-monitor·hw-monitor +
│   │                       #   ADDON 9: log-analyzer·trace-monitor·storage-monitor·bmc-monitor·
│   │                       #   gpu-profiler·capacity-planner·anomaly-detector·net-monitor·
│   │                       #   workload-correlator — 각 app.py+meta.json+guide+zip)
│   └── _templates/        # 신규 Agent 스캐폴드 (_Skeleton, make init)
├── standalone/            # Standalone 배포 (A2A/MCP)
├── deploy/
│   ├── prometheus/        # Prometheus 설정 + 알람 규칙 (deploy/prometheus/rules/)
│   └── helm/              # K8s 배포
├── scripts/               # seed, db-reset, mock GPU exporter (로컬 개발용)
├── sql/
│   ├── sqlite/            # SQLite 스키마 (local)
│   └── pg/                # PostgreSQL 스키마 (dev/staging/prod, docker initdb.d)
├── test/                  # 시험 골격 (dev-env + impl)
└── .docs/                 # PRD + 아키텍처 가이드 + 개발자 가이드
```

## 접속 / 포트

| URL | 설명 |
|-----|------|
| `http://localhost:8100/health` | 헬스체크 |
| `http://localhost:8100/docs` | FastAPI Swagger UI |
| `http://localhost:8100/redoc` | ReDoc |
| `http://localhost:4100` | React 프론트엔드 (dev) |
| `http://localhost:11434` | Ollama API |
| `http://localhost:9090` | Prometheus (메트릭 TSDB·알람 규칙) |
| `http://localhost:9093` | Alertmanager (알람 라우팅 → 백엔드 webhook) |
| `http://localhost:9400/metrics` | mock GPU/HW exporter (로컬 개발용) |
| `http://localhost:3100` | Loki (로그 저장·검색) |
| `http://localhost:16686` | Jaeger UI (OTel 트레이스) |

## API 예시

```bash
TOKEN=$(curl -s -X POST http://localhost:8100/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id":"admin","password":"Admin123!"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# SSE 스트리밍 채팅
curl -X POST http://localhost:8100/api/agent/chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"안녕하세요","history":[]}'

# 사용자 생성
curl -X POST http://localhost:8100/api/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"alice","username":"Alice","password":"Secure123!","role":"user"}'

# Setup Wizard 상태 확인
curl http://localhost:8100/api/setup/status

# Agent 활성화 토글 (admin+)
curl -X PATCH http://localhost:8100/api/agent-config/example \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_enabled": false}'

# Addon Agent ZIP 업로드 (admin+)
curl -X POST "http://localhost:8100/api/addon-agents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@MyAddon.zip"

# 설정 조회 (API Key 마스킹)
curl http://localhost:8100/api/settings/ -H "Authorization: Bearer $TOKEN"

# GPU 메트릭 스냅샷 (utilization/VRAM/온도/전력/XID/ECC)
curl http://localhost:8100/api/metrics/gpu -H "Authorization: Bearer $TOKEN"
# → {"gpus":[{"hostname":"gpu-node-01","gpu":"0","util_percent":87.9,"vram_used_percent":82.3,...}]}

# 서버 하드웨어 스냅샷 (CPU/메모리/RAID/PSU/온도)
curl http://localhost:8100/api/metrics/hardware -H "Authorization: Bearer $TOKEN"

# 활성 알람 목록
curl http://localhost:8100/api/metrics/alerts -H "Authorization: Bearer $TOKEN"

# 관제 Addon Agent 도구 (구현체: addon-agents/zip/)
curl http://localhost:8100/api/addon/gpu-monitor/tools -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/gpu-monitor/tools/get_gpu_snapshot \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
curl http://localhost:8100/api/addon/hw-monitor/status -H "Authorization: Bearer $TOKEN"
# → {"node_count":1,"faulty":0,"healthy":1}

# GPU utilization 시계열 (대시보드 스파크라인용)
curl "http://localhost:8100/api/metrics/gpu/history?minutes=30&step=60" -H "Authorization: Bearer $TOKEN"

# 로그 검색 — Addon-first: log-analyzer addon 경로 사용 (core /api/logs 없음)
curl -X POST http://localhost:8100/api/addon/log-analyzer/tools/search_logs \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"job":"dmesg","keyword":"Xid","minutes":60}'
curl http://localhost:8100/api/addon/log-analyzer/status -H "Authorization: Bearer $TOKEN"
# → {"error_count_1h":0}

# 워크로드 상관 — workload-correlator addon (P2-7, GPU 프로세스↔잡/사용자)
curl -X POST http://localhost:8100/api/addon/workload-correlator/tools/get_usage_by_job \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'

# 네트워크 모니터링 — net-monitor addon (P2-6)
curl -X POST http://localhost:8100/api/addon/net-monitor/tools/get_nic_snapshot \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'

# 이상 탐지 — anomaly-detector addon (P2-5)
curl -X POST http://localhost:8100/api/addon/anomaly-detector/tools/detect_metric_anomalies \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"promql":"DCGM_FI_DEV_GPU_TEMP","hours":6}'
curl -X POST http://localhost:8100/api/addon/anomaly-detector/tools/correlate_alerts \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'

# 용량 계획·효율 — capacity-planner addon (P2-4)
curl -X POST http://localhost:8100/api/addon/capacity-planner/tools/get_efficiency_report \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"hours":24}'
curl -X POST http://localhost:8100/api/addon/capacity-planner/tools/get_underutilized_gpus \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"hours":24,"threshold_percent":10}'

# GPU 프로파일링 — gpu-profiler addon (P2-3, SM/Tensor/DRAM/throttle)
curl -X POST http://localhost:8100/api/addon/gpu-profiler/tools/get_gpu_profile \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'

# BMC/IPMI 조회 — bmc-monitor addon (P2-2, Prometheus+Loki 결합)
curl -X POST http://localhost:8100/api/addon/bmc-monitor/tools/get_bmc_sensors \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
curl -X POST http://localhost:8100/api/addon/bmc-monitor/tools/get_bmc_events \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"level":"error","minutes":120}'

# 스토리지 진단 — storage-monitor addon (P2-1)
curl -X POST http://localhost:8100/api/addon/storage-monitor/tools/get_storage_snapshot \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
# → {"devices":[{"device":"nvme0n1","read_latency_ms":2.15,"iops_read":8838,...}],"raid":[...]}

# 트레이스 조회 — trace-monitor addon
curl -X POST http://localhost:8100/api/addon/trace-monitor/tools/search_traces \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"service":"coresight-g-api","minutes":30}'

# 알람 수신 이력 (Alertmanager → webhook 저장분)
curl "http://localhost:8100/api/alerts/history?limit=20" -H "Authorization: Bearer $TOKEN"
# → {"alerts":[{"alertname":"GPUXidError","severity":"critical","hostname":"gpu-node-01","gpu":"3","status":"firing",...}]}

# PromQL 직접 조회
curl -G http://localhost:8100/api/metrics/query --data-urlencode 'q=DCGM_FI_DEV_GPU_TEMP > 80' \
  -H "Authorization: Bearer $TOKEN"

# 로그아웃 (토큰 블랙리스트)
curl -X POST http://localhost:8100/api/auth/logout -H "Authorization: Bearer $TOKEN"
```

## RBAC 역할

| 역할 | 설명 | 가능한 작업 |
|------|------|------------|
| `supervisor` | 최고 관리자 | 전체 (사용자 삭제 포함) |
| `admin` | 관리자 | 사용자 생성·설정 수정 |
| `user` | 일반 사용자 | 채팅·조회 |
| `viewer` | 뷰어 | 읽기 전용 |

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `passlib + bcrypt ValueError` | bcrypt 4.x passlib 비호환 | `bcrypt>=4.0` 직접 사용 (이미 적용) |
| `ERR_PNPM_IGNORED_BUILDS` | pnpm v10 `package.json` pnpm 필드 미지원 | `front/pnpm-workspace.yaml` 사용 (이미 적용) |
| `port 8100 already in use` | 이전 uvicorn 잔류 | `pkill -f "uvicorn app.main"` |
| Ollama 연결 실패 | `make up` 미실행 | `make up` 후 `curl http://localhost:11434/api/tags` |
| Docker MCP URL이 내부 IP(172.x.x.x)로 반환됨 | 컨테이너 내 IP 자동 감지 한계 | `.env.dev`에 `MCP_HOST=<호스트 IP>` 설정 |
| Docker `/mcp` 404 | nginx `/mcp` 라우팅 미설정 | `front/nginx.conf`에 `/mcp` location 추가 (이미 적용) |
| PostgreSQL `initdb.d` SQL 오류 (`AUTOINCREMENT`) | SQLite 방언 SQL이 PG에 적용됨 | `sql/pg/` 분리 + `docker-compose.yml` 마운트 수정 (이미 적용) |
| pm2 에서 `Failed to spawn: uvicorn` | 프로젝트 디렉터리명 변경으로 `.venv` shebang 경로 깨짐 | `rm -rf .venv && uv sync` 후 `pm2 restart` |
| `/health` 가 `"env":"[object Object]"` 반환 | pm2 데몬(구버전)과 로컬 pm2 버전 불일치 — `env_local` 객체가 소문자 `env` 로 주입 | `pm2 update` |
| `/api/metrics/*` 503 | Prometheus 미기동 | `make up` (prometheus + gpu-mock-exporter 포함) |
| 화면 없는 addon 이 사이드바에 노출 | 메뉴 필터가 `is_active` 만 확인 | `has_front` 필터 추가 (이미 적용) — API 전용 addon 은 메뉴 미노출 |
| 채팅 "에이전트 목록" 에 ADDON 에이전트 누락 | 목록 포맷터가 `tbl_agent_config`(기본+내장 관제)만 조회 | `tbl_addon_agents` 병합 추가 (이미 적용) — 기본/관제/ADDON 3그룹 모두 표시 |
| Addon 재업로드 후 관제 Agent 에 원문 키 이름 중복 행 생성 | `_VALID_TYPES` 에 `"monitoring"` 누락 → agent_type 이 "app" 으로 리셋되며 Addon-first 가드 우회 | `_VALID_TYPES` 에 `"monitoring"` 추가 (이미 적용) |

## 커스터마이즈

1. 관제 Agent 구현체는 core 가 아닌 `addon-agents/zip/<agent>/` 에 둔다 —
   `<agent>-app.py` 가 `router` + `_TOOLS` + `TOOL_EXECUTORS` + `SYSTEM_PROMPT` 를 export (규약)
   - **대시보드 위젯 규약**: addon 이 `GET /status` 를 구현하면 활성화 시 대시보드
     "관제 Agent 위젯" 카드로 자동 표시 (상위 숫자/문자 필드). 미구현 시 자동 스킵 — 오류 없음
2. `app/agents/orchestrator.py` → `_VALID_INTENTS`, `_AGENT_MAP`(`addon_agent_cls("<agent>", "<intent>")`), `_CLASSIFY_SYSTEM` 수정
3. `sql/sqlite/01_init.sql` + `sql/pg/01_init.sql` → 도메인 테이블 추가 (양쪽 동기화)
4. `front/src/App.tsx` → 도메인 페이지 추가

자세한 내용: [`.docs/guides/02-development.md`](.docs/guides/02-development.md)

## 프론트엔드 페이지

| 경로 | 설명 | 권한 |
|------|------|------|
| `/setup` | Setup Wizard (Supervisor 생성 → **TOTP 2FA** → LLM 설정) | 인증 불필요 |
| `/login` | 로그인 (TOTP 2단계 인증 지원) | 인증 불필요 |
| `/dashboard` | 통합 관제 대시보드 (활성 알람 + GPU 카드/스파크라인 + HW 노드 테이블, 15s 폴링, 기본 진입) | 로그인 |
| `/chat` | AI Assistant (세션 관리, 모델 선택, SSE 스트리밍) | 로그인 |
| `/agents` | 에이전트 관리 (활성화 토글, Addon ZIP 업로드, MCP 상태·가이드·설정 수정·삭제) | admin+ |
| `/users` | 사용자 관리 (CRUD) | admin+ |
| `/settings` | 시스템 설정 (LLM 연결 테스트) | admin+ |
| `/profile` | 마이페이지 (프로필·비밀번호·**TOTP 2FA** 관리) | 로그인 |

## 구현 현황

| Phase | 범위 | 상태 |
|-------|------|------|
| 1 | 인증(F5) · 사용자관리 · 설정(F9) | ✅ PASS (test/impl/1) |
| 2 | 로그인 UI · 채팅 UI · SSE 스트리밍(F7) | ✅ PASS (test/impl/2) |
| 3 | Setup Wizard API(F6) · Agent Config(F8) · Addon Agent ZIP(F4) | ✅ PASS (test/impl/3) |
| 4 | Setup Wizard UI · AppLayout · Agents/Users/Settings 관리 페이지 | ✅ PASS (test/impl/4) |
| 5 | F12 — A2A Protocol v1.0 · MCP JSON-RPC 2.0 · Agent Registry | ✅ PASS (test/impl/5) |
| 6 | F13~F16 — TOTP · 테마 · 마이페이지 · 설정 UI · Addon toggle · 필수 에이전트 배지 | ✅ 완료 |
| 7 | F17~F19 — AI 환각 방지 · 맞춤지침(시스템/사용자) · UI 다국어(한국어/영어) | ✅ 완료 |
| 8 | F20~F21 + F12 재설계 — 키워드 룰셋 · Addon API 가드 · MCP Proxy per-agent · MCP 상태(green/orange/red) · MCP 설정 CRUD · MCP 가이드/수정/삭제 UI | ✅ PASS (test/impl/6) |
| 9 (v2) | F22 Agent 카탈로그 — agent_type 9종 · `-meta.json` 표준 · catalog API · scaffold API · 4종 템플릿(Board/Service/ToolProxy/RAG) · BUG-v1.4-01 sql_path 수정 | ✅ PASS (test/impl/8) |
| 10 (v2) | F23 Registry v2 — capability 기반 검색 · Agent Card · heartbeat/lease · lifecycle_state · tbl_addon_agent_capabilities · addon 업로드 시 capabilities 자동 저장 | ✅ PASS (test/impl/9) |
| 11 (v2) | F24 Agent Builder UI — 4단계 Wizard · 9종 유형 카드 선택 · scaffold ZIP 다운로드/즉시배포 · domain 직접 치환 버그 수정 | ✅ PASS (test/impl/10) |
| 12 (v2) | F25 Orchestrator 고도화 — capability 기반 Registry 동적 라우팅 · Reviewer Gate · HITL 게이트 · SSE 이벤트(registry_miss/hitl_pending/review_gate) · 옵트인 설정 | ✅ PASS (test/impl/11) |
| 13 (v2) | UI 통합 — "새 Agent 만들기" + "Addon 에이전트 등록" 단일 모달 통합 · 탭 구조(스캐폴딩/ZIP 업로드) · .omc 시스템 파일 필터 | ✅ PASS (test/impl/12) |
| 14 (v2) | LLM 설정 우선순위 버그 수정 — .env.* 파일 값이 DB보다 우선 적용 (os.environ > .env > DB > 기본값) | ✅ PASS (test/impl/13) |

## 구현된 엔드포인트

| 경로 | 메서드 | 설명 | 권한 |
|------|--------|------|------|
| `/health` | GET | 헬스체크 | 없음 |
| `/api/auth/login` | POST | 로그인 → JWT (TOTP 지원) | 없음 |
| `/api/auth/logout` | POST | 로그아웃 (블랙리스트) | Bearer |
| `/api/auth/me` | GET | 내 프로필 조회 | Bearer |
| `/api/auth/me` | PATCH | 프로필·비밀번호 변경 | Bearer |
| `/api/auth/totp/qr` | GET | TOTP QR 코드 URI 발급 | Bearer |
| `/api/auth/totp/enable` | POST | TOTP 활성화 (코드 검증) | Bearer |
| `/api/auth/totp/disable` | POST | TOTP 비활성화 (코드 검증) | Bearer |
| `/api/users/` | GET/POST | 사용자 목록·생성 | admin+ |
| `/api/users/{id}` | DELETE | 사용자 삭제 | supervisor |
| `/api/agent/chat` | POST | 비스트리밍 채팅 | Bearer |
| `/api/agent/chat/stream` | POST | SSE 스트리밍 채팅 | Bearer |
| `/api/settings/` | GET | 설정 조회 (마스킹) | Bearer |
| `/api/settings/{key}` | PUT | 설정 변경 | admin+ |
| `/api/settings/test-llm` | POST | LLM 연결 테스트 | Bearer |
| `/api/setup/status` | GET | Setup Wizard 상태 | 없음 |
| `/api/setup/supervisor` | POST | 최초 Supervisor 생성 | 없음 |
| `/api/setup/llm-provider` | PUT | LLM 설정 저장 | 없음 |
| `/api/setup/complete` | POST | Setup 완료 마킹 | 없음 |
| `/api/agent-config/` | GET | Agent 설정 목록 | Bearer |
| `/api/agent-config/{key}` | GET/PATCH | Agent 설정 조회·변경 | Bearer/admin+ |
| `/api/addon-agents/` | GET | Addon 목록 | Bearer |
| `/api/addon-agents/upload` | POST | ZIP 업로드·핫 디플로이 | admin+ |
| `/api/addon-agents/{key}` | DELETE | Addon 삭제 | admin+ |
| `/api/addon-agents/{key}` | PATCH | Addon 이름 수정 | admin+ |
| `/api/addon-agents/{key}/toggle` | PATCH | Addon 활성/비활성 토글 | admin+ |
| `/api/addon-agents/templates/list` | GET | 템플릿 목록 (agent_type 포함) | Bearer |
| `/api/addon-agents/templates/download/{name}` | GET | 템플릿 ZIP 다운로드 | Bearer |
| `/api/addon-agents/catalog` | GET | Agent 카탈로그 (유형별 그룹) | Bearer |
| `/api/addon-agents/scaffold` | POST | 스캐폴딩 ZIP 생성·다운로드 | Bearer |
| `/api/addon-agents/guide` | GET | Addon 개발 가이드 (README.md) | Bearer |
| `/api/addon/{key}/*` | ANY | 동적 Addon 라우터 (활성 시에만) | Bearer |
| `/.well-known/agent-card.json` | GET | A2A AgentCard | 없음 |
| `/a2a/tasks` | POST | A2A Task 생성 | Bearer |
| `/a2a/tasks/{id}` | GET | A2A Task SSE 스트림 | Bearer |
| `/a2a/tasks/{id}/result` | GET | A2A Task 결과 | Bearer |
| `/mcp` | POST | MCP JSON-RPC 2.0 (통합) | Bearer |
| `/mcp/guide` | GET | MCP 가이드 + 클라이언트 설정 | 없음 |
| `/mcp/{agent_key}` | POST | MCP JSON-RPC 2.0 (에이전트별) | Bearer |
| `/mcp/{agent_key}/guide` | GET | 에이전트별 MCP 가이드 | 없음 |
| `/api/mcp-configs/` | GET | MCP 설정 목록 | Bearer |
| `/api/mcp-configs/{key}` | GET | MCP 설정 조회 | Bearer |
| `/api/mcp-configs/{key}` | PUT | MCP 설정 등록/수정 (upsert) | admin+ |
| `/api/mcp-configs/{key}` | DELETE | MCP 매핑 삭제 (에이전트 유지) | admin+ |
| `/api/mcp-configs/{key}/status` | GET | MCP 상태 (green/orange/red) | Bearer |
| `/api/agent-registry/` | GET/POST | 외부 Agent 목록·등록 | admin+ |
| `/api/agent-registry/{key}` | DELETE | 외부 Agent 해제 | admin+ |
| `/api/agent-registry/{key}/ping` | POST | 연결 테스트 | admin+ |
| `/api/agent-registry/search` | POST | capability/verb/domain/type 기반 검색 | admin+ |
| `/api/agent-registry/{key}/card` | GET | Agent Card 조회 (자동생성 또는 저장값) | admin+ |
| `/api/agent-registry/{key}/card` | PUT | Agent Card JSON 직접 업데이트 | admin+ |
| `/api/agent-registry/{key}/heartbeat` | POST | Heartbeat 갱신 + lease 연장 | admin+ |
| `/api/agent-registry/{key}/health` | GET | 실시간 헬스 상태 (health_dot, lease_expired) | admin+ |

## Addon Agent 카탈로그 (v2)

9종 Agent 유형을 ZIP으로 패키징하여 등록·확장 가능.

| 유형 | 템플릿 | 역할 |
|------|--------|------|
| `app` | Board | FE+BE+DB 완결형 업무 앱 (게시판 등) |
| `service` | ServiceAgent | 백엔드 비즈니스 로직 전용 |
| `tool-proxy` | ToolProxyAgent | 외부 REST API → MCP 어댑터 |
| `rag` | RagAgent | 문서 임베딩 + 벡터 검색 Q&A |
| `reviewer` | — | 품질 검수·환각 탐지 (템플릿 준비 중) |
| `execution` | — | 코드 실행·배치 잡 (템플릿 준비 중) |
| `hitl` | — | 사람 승인 게이트웨이 (템플릿 준비 중) |
| `memory` | — | 장기 상태·사용자 선호 관리 (템플릿 준비 중) |
| `federation` | — | 외부 A2A/MCP Agent 연동 (템플릿 준비 중) |

### -meta.json 표준

ZIP 내 `{AgentName}-meta.json` 포함 시 유형 자동 인식:

```json
{
  "agent_type": "service",
  "version": "1.0.0",
  "description": "비즈니스 로직 처리",
  "capabilities": [
    {
      "verb": "process",
      "domain": "service.my-domain",
      "description": "입력 처리 후 결과 반환"
    }
  ],
  "governance": {"data_classification": "internal"},
  "required_env": [],
  "optional_env": ["ANTHROPIC_API_KEY"]
}
```

`-meta.json` 없으면 `agent_type: "app"` 기본 적용 (v1.4 하위 호환).

### 스캐폴딩

```bash
# 새 Service Agent 스캐폴딩 ZIP 다운로드
curl -X POST http://localhost:8100/api/addon-agents/scaffold \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_name":"MyAnalytics","agent_type":"service","description":"데이터 분석 처리"}' \
  -o MyAnalytics.zip

# 바로 업로드
curl -X POST "http://localhost:8100/api/addon-agents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@MyAnalytics.zip"

# 카탈로그 조회 (유형별 그룹)
curl http://localhost:8100/api/addon-agents/catalog \
  -H "Authorization: Bearer $TOKEN"

# 유형 필터
curl "http://localhost:8100/api/addon-agents/catalog?agent_type=service" \
  -H "Authorization: Bearer $TOKEN"
```

## Agent Registry v2 (F23)

외부 Standalone Agent를 등록하고 capability 기반으로 검색·관리.

### 외부 Agent 등록

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

### capability 기반 검색

```bash
# verb 기반 검색
curl -X POST http://localhost:8100/api/agent-registry/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"capabilities": ["retrieve"], "lifecycle_state": "active"}'

# domain 접두어 + agent_type 필터
curl -X POST http://localhost:8100/api/agent-registry/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain_prefix": "knowledge.", "agent_type": "rag"}'
```

### Agent Card · Heartbeat · Health

```bash
# Agent Card 조회 (없으면 자동 생성)
curl http://localhost:8100/api/agent-registry/hr-rag-agent/card \
  -H "Authorization: Bearer $TOKEN"

# Heartbeat 갱신 (lease 30분 연장, quarantined → active 복구)
curl -X POST http://localhost:8100/api/agent-registry/hr-rag-agent/heartbeat \
  -H "Authorization: Bearer $TOKEN"

# 헬스 상태 조회 (health_dot: green/orange/red)
curl http://localhost:8100/api/agent-registry/hr-rag-agent/health \
  -H "Authorization: Bearer $TOKEN"
```

### lifecycle_state

| 상태 | 설명 | health_dot |
|------|------|-----------|
| `active` | 정상 운영 | green |
| `quarantined` | 장애·격리 (heartbeat 시 복구) | red |
| `retired` | 폐기 | red |
| `draft` | 등록 준비 중 | orange |

## 개발자 가이드

| 가이드 | 대상 |
|--------|------|
| [G1: 시작](.docs/guides/01-getting-started.md) | 신규 사용자 |
| [G2: 확장 개발](.docs/guides/02-development.md) | 개발자 |
| [G3: 시험](.docs/guides/03-testing.md) | 개발자·QA |
| [G4: 배포](.docs/guides/04-deployment.md) | DevOps |
| [G5: 운영](.docs/guides/05-operations.md) | 관리자 |
| [G6: Standalone A2A/MCP](.docs/guides/06-standalone.md) | 개발자·DevOps |

## MCP Proxy

**필수 에이전트를 제외한 내장 토글 에이전트 + Addon 에이전트** 전체가 활성화 시 독립 MCP 서버로 노출됩니다.

```bash
# MCP 설정 등록 (포트 + 커스텀 인자)
curl -X PUT http://localhost:8100/api/mcp-configs/{agent_key} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"port": 20001, "extra_args": ["--header:x-api-key:token"]}'

# MCP 상태 확인 (green/orange/red)
curl http://localhost:8100/api/mcp-configs/{agent_key}/status \
  -H "Authorization: Bearer $TOKEN"

# 에이전트별 MCP 가이드 (상태, tool 목록, 클라이언트 설정 스니펫)
curl http://localhost:8100/mcp/{agent_key}/guide

# MCP 핸드셰이크 → tool 목록 조회
curl -X POST http://localhost:8100/mcp/{agent_key} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

**Claude Desktop 연동 (mcp-remote 브리지):**

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

**MCP Proxy URL 포맷:**

프록시 포트가 등록되면 URL은 `http://{서버IP}:{proxy_port}/mcp` 형태로 제공됩니다.  
브라우저가 `window.location.hostname`으로 실제 서버 IP를 자동 판별합니다.  
포트 미등록 시 status = 🔴 (`red`) — 포트 없이는 "정상 매핑"으로 표시되지 않습니다.

**에이전트 관리 UI (`/agents`):**

활성화된 모든 비필수 에이전트(내장 토글 + Addon) 행에 MCP 서브 기능 표시:
- `●` — MCP 상태 dot: 🟢 녹색(포트+에이전트 모두 활성) · 🟠 주황(대기/연결 중) · 🔴 빨강(포트 미설정/오류) — 4초 폴링
- `ⓘ` — MCP 가이드 모달: URL, 상태 배너, tool 목록, Claude Desktop/Cursor/VSCode 설정 + 복사 버튼
- `✎` — MCP 설정 수정: 포트(선택) + 커스텀 인자(key:value 행 추가/삭제)
- `✕` — MCP 매핑 삭제 (에이전트 유지, MCP 제공 중단)

## 다음 단계 (PRD 잔여)

- PostgreSQL 전환 시 Alembic 마이그레이션
- Redis JWT 블랙리스트 (현재 in-memory)
- GitHub Actions CI 파이프라인 완성

## 참조

- [PRD](.docs/Multi%20AI%20Agent%20Standard-PRD.md)
- [아키텍처 가이드](Multi%20AI%20Agent%20아키텍처%20가이드%20v1.0.md)
- [시작 가이드](.docs/guides/01-getting-started.md)
- [참조 구현: SmartHaccp-MultiAgent](https://github.com/edentns/SmartHaccp-MultiAgent)
