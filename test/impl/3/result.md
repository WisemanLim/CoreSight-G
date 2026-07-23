# 시험 결과 — Phase 3

> **수행일:** 2026-06-23
> **환경:** local (SQLite, Python 3.13)
> **명령:** `uv run pytest test/impl/3/test_phase3.py -v`

## 결과 요약

| ID  | 항목 | 결과 |
|-----|------|------|
| T1  | GET /api/setup/status — 초기 상태 | ✅ PASS |
| T2  | POST /api/setup/supervisor — 중복 → 409 | ✅ PASS |
| T3  | PUT /api/setup/llm-provider | ✅ PASS |
| T4  | POST /api/setup/complete | ✅ PASS |
| T5  | GET /api/setup/status — 완료 후 | ✅ PASS |
| T6  | GET /api/agent-config/ — example 포함 | ✅ PASS |
| T7  | PATCH /api/agent-config/example is_enabled=false | ✅ PASS |
| T8  | GET /api/agent-config/example — is_enabled=0 | ✅ PASS |
| T9  | PATCH /api/agent-config/example 재활성화 | ✅ PASS |
| T10 | GET /api/addon-agents/ — 초기 빈 목록 | ✅ PASS |
| T11 | POST /api/addon-agents/upload ExampleAddon.zip | ✅ PASS |
| T12 | GET /api/addon-agents/ — 1건 확인 | ✅ PASS |
| T13 | GET /api/addon/exampleaddon/items — 핫 로드 | ✅ PASS |
| T14 | POST /api/addon-agents/upload 재시도 force=false → 409 | ✅ PASS |
| T15 | DELETE /api/addon-agents/exampleaddon | ✅ PASS |
| T16 | GET /api/addon-agents/ — 삭제 후 빈 목록 | ✅ PASS |
| T17 | POST /api/addon-agents/upload viewer 권한 → 403 | ✅ PASS |
| T18 | POST /api/addon-agents/upload '..' 경로 포함 → 400 | ✅ PASS |

## 판정: **PASS** (18/18)

## 수정 이력

| 이슈 | 원인 | 수정 |
|------|------|------|
| `no such column: model` | `apply_column_migrations()` 가 lifespan에서만 실행 — 테스트에서 ASGI lifespan 미호출 | `client` 픽스처에서 `run_migrations()` + `apply_column_migrations()` 직접 호출 |
| `addon_loader app 미초기화` | `_app` 세팅도 lifespan(`addon_init`) 의존 | `client` 픽스처에서 `addon_init(app)` 직접 호출 |

## 생성·수정 파일

| 파일 | 유형 |
|------|------|
| `sql/01_init.sql` | 수정 — tbl_agent_config에 model, system_prompt 컬럼 추가 |
| `app/db.py` | 수정 — `apply_column_migrations()` 추가 |
| `app/routers/router_setup.py` | 신규 — F6 Setup Wizard API |
| `app/routers/router_agent_config.py` | 신규 — F8 Agent Config 관리 |
| `app/routers/router_addon_agent.py` | 수정 — F4 Addon Agent 전체 구현 |
| `app/addon_agent_loader.py` | 수정 — `_load_all_from_disk()` DB 연동 |
| `app/main.py` | 수정 — 신규 라우터 등록 |
| `test/impl/3/scenario.md` | 신규 |
| `test/impl/3/test_phase3.py` | 신규 |
