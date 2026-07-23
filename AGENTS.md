# AGENTS.md — coresight-g

> AI 코딩 어시스턴트(Claude Code, Cursor 등)를 위한 프로젝트 표준 가이드

## 프로파일

```
wise-dev-standard / python-fastapi × ict-saas
참조 구현: SmartHaccp-MultiAgent
```

## 스택 요약

| 레이어 | 기술 |
|--------|------|
| Backend | FastAPI 0.115+ · Python 3.12 · uv · SQLAlchemy 2 · Alembic |
| Frontend | Vite + React 19 + TypeScript 5.8 + Tailwind v4 · react-router v7 |
| DB | SQLite (local) / PostgreSQL 17 (dev+) + Redis 7.4 |
| LLM | Anthropic SDK (primary) · Ollama REST (fallback) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| AI 구조 | Orchestrator (sonnet) + BaseAgent (haiku) + Addon Hot-deploy |

## [CUSTOMIZE] 포인트

구현 시 반드시 수정해야 할 파일:

| 파일 | 수정 내용 |
|------|-----------|
| `app/agents/orchestrator.py` | `_VALID_INTENTS`, `_AGENT_MAP`, `_AGENT_LABELS` |
| `app/agents/example_agent.py` | 도메인 시스템 프롬프트, Tool 목록, executor |
| `app/tools/example_tools.py` | Tool 실행 함수 (DB 쿼리, 외부 API) |
| `app/core/config.py` | `app_name`, 추가 설정값 |
| `front/src/App.tsx` | 도메인 페이지/라우트 |
| `sql/01_init.sql` | 도메인 테이블 추가 |

## 개발 규칙

- 라우터: `app/routers/router_*.py` 패턴 준수
- 의존성: `uv add` 사용 (`pip install` 직접 금지)
- 프론트 패키지: `pnpm add` 사용
- DB 마이그레이션: `sql/*.sql` 파일 순번 추가 (모두 idempotent)
- 시험: `test/dev-env/` + `test/impl/<Nth>/` 구조 준수
- 환경변수: `.env.local` 수정. `.env.prod` 는 키 목록만

## 참조

- PRD: `.docs/Multi AI Agent Standard-PRD.md`
- 아키텍처: `.docs/Multi AI Agent 아키텍처 가이드 v1.0.md` (루트 위치)
- 가이드: `.docs/guides/` (01~06)
