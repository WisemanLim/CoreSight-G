# 시험 시나리오 — Phase 3 (Setup Wizard · Agent Config · Addon Agent)

> **차수:** 3
> **범위:** F6 Setup Wizard API, F8 Agent Config 관리, F4 Addon Agent ZIP 업로드·핫 디플로이

## 시험 항목

| ID  | 항목 | 검증 포인트 |
|-----|------|------------|
| T1  | GET /api/setup/status — 초기 | has_supervisor=true, completed=false |
| T2  | POST /api/setup/supervisor — 중복 | 409 반환 (admin 이미 존재) |
| T3  | PUT /api/setup/llm-provider | 200, 설정 저장 확인 |
| T4  | POST /api/setup/complete | 200, setup_completed=true |
| T5  | GET /api/setup/status — 완료 후 | completed=true |
| T6  | GET /api/agent-config/ — 목록 | 200, 'example' Agent 포함 |
| T7  | PATCH /api/agent-config/example is_enabled=false | 200 |
| T8  | GET /api/agent-config/example — 비활성화 확인 | is_enabled=0 |
| T9  | PATCH /api/agent-config/example is_enabled=true (복원) | 200 |
| T10 | GET /api/addon-agents/ — 초기 빈 목록 | 200, addons=[] |
| T11 | POST /api/addon-agents/upload ExampleAddon.zip | 200, api_prefix 반환 |
| T12 | GET /api/addon-agents/ — 등록 확인 | 1건 포함 |
| T13 | GET /api/addon/exampleaddon/items — 핫 로드 | 200, items 응답 |
| T14 | POST /api/addon-agents/upload 재시도 force=false | 409 반환 |
| T15 | DELETE /api/addon-agents/exampleaddon | 200 |
| T16 | GET /api/addon-agents/ — 삭제 후 확인 | 빈 목록 |
| T17 | POST /api/addon-agents/upload — viewer 권한 | 403 반환 |
| T18 | POST /api/addon-agents/upload — '..' 경로 포함 ZIP | 400 반환 |

## 실행 명령

```bash
uv run pytest test/impl/3/test_phase3.py -v
```
