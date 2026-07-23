# coresight-g — python-fastapi (wise-dev-standard / python-fastapi)
# 참조 구현: SmartHaccp-MultiAgent
.PHONY: dev dev-be dev-fe test build deploy up down standalone docker-standalone \
        local-all local-stop local-logs local-status \
        dev-all dev-stop dev-logs \
        staging-all staging-stop staging-logs \
        prod-all prod-stop prod-logs \
        db-reset seed db-fresh
ENV ?= local

# 포트를 .env.* 에서 읽는 헬퍼 (Makefile 변수, 레시피 외부에서 평가됨)
_port = $(shell grep '^$(1)=' .env.$(ENV) 2>/dev/null | cut -d= -f2 | tr -d '"' | tr -d "'" | xargs)

# ── 인프라 단독 (하위 호환) ───────────────────────────────────────────────────
up:      ## 인프라만 기동 (postgres + redis + ollama)
	@bash scripts/ollama_preflight.sh .env.$(ENV)
	@if docker ps --format '{{.Names}}' 2>/dev/null | grep -q 'ollama'; then \
		docker compose --env-file .env.$(ENV) up -d; \
	else \
		docker compose --env-file .env.$(ENV) up -d postgres redis; \
	fi

down:    ## 전체 컨테이너 정리
	docker compose --env-file .env.$(ENV) --profile app --profile web down --remove-orphans

# ── 개발 서버 직접 실행 (터미널 분리용) ──────────────────────────────────────
dev-be:  ## 백엔드만 직접 실행 (uv + uvicorn --reload)
	@BACKEND_PORT=$$(grep '^BACKEND_PORT=' .env.$(ENV) 2>/dev/null | cut -d= -f2 | tr -d '"' | tr -d "'" || echo 8100); \
	uv run uvicorn app.main:app --reload --port $${BACKEND_PORT:-8100}

dev-fe:  ## 프론트엔드만 실행 (pnpm dev)
	@FRONTEND_PORT=$$(grep '^FRONTEND_PORT=' .env.$(ENV) 2>/dev/null | cut -d= -f2 | tr -d '"' | tr -d "'" || echo 4100); \
	cd front && pnpm dev --port $${FRONTEND_PORT:-4100}

dev:     ## 전체 개발환경 안내 (infra 기동 후 터미널 안내)
	@bash scripts/ollama_preflight.sh .env.$(ENV)
	@if docker ps --format '{{.Names}}' 2>/dev/null | grep -q 'ollama'; then \
		docker compose --env-file .env.$(ENV) up -d; \
	else \
		docker compose --env-file .env.$(ENV) up -d postgres redis; \
	fi
	@BACKEND_PORT=$$(grep '^BACKEND_PORT=' .env.$(ENV) 2>/dev/null | cut -d= -f2 | tr -d '"' | tr -d "'" || echo 8100); \
	FRONTEND_PORT=$$(grep '^FRONTEND_PORT=' .env.$(ENV) 2>/dev/null | cut -d= -f2 | tr -d '"' | tr -d "'" || echo 4100); \
	echo "▶ Backend  → http://localhost:$${BACKEND_PORT:-8100}  (make dev-be)"; \
	echo "▶ Frontend → http://localhost:$${FRONTEND_PORT:-4100}  (make dev-fe)"; \
	echo "또는: make local-all  (pm2 백그라운드 통합 실행)"

# ── local — SQLite + Ollama(Docker) + BE/FE (pm2 비Docker) ───────────────────
local-all: ## local 전체 기동: Ollama Docker + BE/FE pm2 (SQLite 자동)
	@command -v pm2 >/dev/null 2>&1 || (echo "❌ pm2 필요: npm i -g pm2" && exit 1)
	mkdir -p logs
	@bash scripts/ollama_preflight.sh .env.$(ENV)
	@BACKEND_PORT=$$(grep '^BACKEND_PORT=' .env.$(ENV) 2>/dev/null | cut -d= -f2 | tr -d '"' | tr -d "'" || echo 8100); \
	FRONTEND_PORT=$$(grep '^FRONTEND_PORT=' .env.$(ENV) 2>/dev/null | cut -d= -f2 | tr -d '"' | tr -d "'" || echo 4100); \
	ENV=local BACKEND_PORT=$$BACKEND_PORT FRONTEND_PORT=$$FRONTEND_PORT \
		pm2 start ecosystem.config.js --env local
	pm2 save
	@BACKEND_PORT=$$(grep '^BACKEND_PORT=' .env.$(ENV) 2>/dev/null | cut -d= -f2 | tr -d '"' | tr -d "'" || echo 8100); \
	FRONTEND_PORT=$$(grep '^FRONTEND_PORT=' .env.$(ENV) 2>/dev/null | cut -d= -f2 | tr -d '"' | tr -d "'" || echo 4100); \
	echo "▶ Backend  → http://localhost:$${BACKEND_PORT:-8100}"; \
	echo "▶ Frontend → http://localhost:$${FRONTEND_PORT:-4100}"; \
	echo "▶ 로그: make local-logs"

local-stop: ## local 전체 중단 (pm2 + ollama)
	pm2 stop ecosystem.config.js || true
	docker compose --env-file .env.$(ENV) stop ollama

local-logs: ## local 로그 모니터링 (pm2)
	pm2 logs

local-status: ## local 프로세스 상태 (pm2)
	pm2 status

# ── dev — PostgreSQL + Redis + Ollama + BE + FE (Docker Compose) ──────────────
dev-all: ## dev 전체 기동 (.env.dev, docker compose)
	@bash scripts/ollama_preflight.sh .env.dev
	@if docker ps --format '{{.Names}}' 2>/dev/null | grep -q 'ollama'; then \
		docker compose --env-file .env.dev --profile app --profile web up -d; \
	else \
		docker compose --env-file .env.dev --profile app --profile web up -d --scale ollama=0; \
	fi

dev-stop: ## dev 전체 중단
	docker compose --env-file .env.dev --profile app --profile web down

dev-logs: ## dev 로그 모니터링 (docker compose)
	docker compose --env-file .env.dev --profile app --profile web logs -f

# ── staging ───────────────────────────────────────────────────────────────────
staging-all: ## staging 전체 기동 (.env.staging, docker compose)
	@bash scripts/ollama_preflight.sh .env.staging
	@if docker ps --format '{{.Names}}' 2>/dev/null | grep -q 'ollama'; then \
		docker compose --env-file .env.staging --profile app --profile web up -d; \
	else \
		docker compose --env-file .env.staging --profile app --profile web up -d --scale ollama=0; \
	fi

staging-stop: ## staging 전체 중단
	docker compose --env-file .env.staging --profile app --profile web down

staging-logs: ## staging 로그 모니터링
	docker compose --env-file .env.staging --profile app --profile web logs -f

# ── prod ──────────────────────────────────────────────────────────────────────
prod-all: ## prod 전체 기동 (.env.prod, docker compose)
	@bash scripts/ollama_preflight.sh .env.prod
	@if docker ps --format '{{.Names}}' 2>/dev/null | grep -q 'ollama'; then \
		docker compose --env-file .env.prod --profile app --profile web up -d; \
	else \
		docker compose --env-file .env.prod --profile app --profile web up -d --scale ollama=0; \
	fi

prod-stop: ## prod 전체 중단
	docker compose --env-file .env.prod --profile app --profile web down

prod-logs: ## prod 로그 모니터링
	docker compose --env-file .env.prod --profile app --profile web logs -f api

# ── DB 관리 ───────────────────────────────────────────────────────────────────
db-reset: ## DB 데이터 삭제 + 스키마 재생성 (Setup Wizard 재시험용)
	uv run python scripts/db_reset.py

seed:    ## 기본 설정 + 테스트 계정 삽입 (supervisor:admin/Admin123!)
	uv run python scripts/seed.py

db-fresh: ## db-reset + seed (완전 초기화 후 테스트 데이터 삽입)
	uv run python scripts/db_reset.py
	uv run python scripts/seed.py

# ── CI / 품질 ─────────────────────────────────────────────────────────────────
test:    ## pytest 실행
	uv run pytest

lint:    ## ruff 검사
	uv run ruff check .

# ── 빌드 / 배포 ───────────────────────────────────────────────────────────────
build:   ## 앱 이미지 빌드 (profiles:app + web)
	docker compose --env-file .env.$(ENV) --profile app --profile web build

deploy:  ## Helm 배포
	helm upgrade --install coresight-g ./deploy/helm

standalone:  ## Standalone Agent 패키징 (make standalone AGENT=MyAgent)
	@echo "Usage: AGENT=MyAgent make standalone"
	@test -n "$(AGENT)" || (echo "AGENT 변수 필요" && exit 1)
	@cd standalone && $(MAKE) AGENT=$(AGENT)

docker-standalone: ## Standalone Agent 도커 이미지 빌드
	@test -n "$(AGENT)" || (echo "AGENT 변수 필요" && exit 1)
	docker build -f standalone/Dockerfile.standalone \
	  --build-arg AGENT_KEY=$(shell echo $(AGENT) | tr '[:upper:]' '[:lower:]') \
	  -t wise-agent-$(shell echo $(AGENT) | tr '[:upper:]' '[:lower:]'):latest .
