# Phase 4 시험 시나리오 — Frontend Management Pages

**구현 범위:** Setup Wizard UI · Agent 관리 UI · 사용자 관리 UI · 시스템 설정 UI · AppLayout

**시험 방식:** 프론트엔드 UI는 `pnpm build` 타입 검증 + 백엔드 API 통합 시험 (프론트가 호출하는 엔드포인트 검증)

---

## T1: Setup 상태 — supervisor 존재 시

| 항목 | 내용 |
|------|------|
| 대상 | `GET /api/setup/status` |
| 조건 | DB에 supervisor 존재 |
| 기댓값 | `{"has_supervisor": true, "completed": true/false}` |

## T2: 사용자 목록 조회 (supervisor)

| 항목 | 내용 |
|------|------|
| 대상 | `GET /api/users/` |
| 조건 | supervisor 토큰 |
| 기댓값 | `{"users": [...], "total": N}` — admin 포함 |

## T3: 사용자 생성 (supervisor)

| 항목 | 내용 |
|------|------|
| 대상 | `POST /api/users/` |
| Body | `{user_id: "u4_test", username: "테스트", password: "Test123!", role: "user"}` |
| 기댓값 | 201 |

## T4: 사용자 목록 — 생성 후 포함 확인

| 항목 | 내용 |
|------|------|
| 대상 | `GET /api/users/` |
| 기댓값 | users 배열에 `u4_test` 포함 |

## T5: 중복 사용자 ID 생성 → 409

| 항목 | 내용 |
|------|------|
| 대상 | `POST /api/users/` with same user_id |
| 기댓값 | 409 Conflict |

## T6: 비인증 사용자 목록 조회 → 401

| 항목 | 내용 |
|------|------|
| 대상 | `GET /api/users/` — No auth |
| 기댓값 | 401 |

## T7: viewer 권한으로 사용자 목록 조회 → 403

| 항목 | 내용 |
|------|------|
| 대상 | `GET /api/users/` — viewer token |
| 기댓값 | 403 |

## T8: admin 권한으로 사용자 삭제 시도 → 403

| 항목 | 내용 |
|------|------|
| 대상 | `DELETE /api/users/u4_test` — admin token |
| 조건 | admin-role 사용자 토큰 (supervisor가 아님) |
| 기댓값 | 403 |

## T9: supervisor 권한으로 사용자 삭제 → 200

| 항목 | 내용 |
|------|------|
| 대상 | `DELETE /api/users/u4_test` — supervisor token |
| 기댓값 | 200 |

## T10: 설정 목록 조회

| 항목 | 내용 |
|------|------|
| 대상 | `GET /api/settings/` |
| 조건 | 인증 토큰 |
| 기댓값 | `{"settings": [...]}` — API Key 마스킹 확인 |

## T11: 설정 변경 (supervisor)

| 항목 | 내용 |
|------|------|
| 대상 | `PUT /api/settings/ollama_model` |
| Body | `{"value": "llama3.2-test", "description": ""}` |
| 기댓값 | 200 |

## T12: 설정 변경 후 조회 — 업데이트 확인

| 항목 | 내용 |
|------|------|
| 대상 | `GET /api/settings/` |
| 기댓값 | `ollama_model` 값이 `llama3.2-test` |

## T13: LLM 연결 테스트 엔드포인트

| 항목 | 내용 |
|------|------|
| 대상 | `POST /api/settings/test-llm` |
| 기댓값 | 200, `{"ollama": bool, "anthropic_configured": bool}` |

## T14: Setup Wizard — supervisor 이미 존재 시 409

| 항목 | 내용 |
|------|------|
| 대상 | `POST /api/setup/supervisor` (no auth) |
| Body | `{user_id: "another_sv", username: "X", password: "X123456!"}` |
| 기댓값 | 409 (supervisor already exists) |

## T15: Setup LLM Provider (no auth) — 멱등

| 항목 | 내용 |
|------|------|
| 대상 | `PUT /api/setup/llm-provider` (no auth) |
| Body | default values |
| 기댓값 | 200 (idempotent upsert) |

## T16: Setup Complete (no auth) — 멱등

| 항목 | 내용 |
|------|------|
| 대상 | `POST /api/setup/complete` (no auth) |
| 기댓값 | 200, `{"setup_completed": true}` |

## T17: Setup 완료 후 status 확인

| 항목 | 내용 |
|------|------|
| 대상 | `GET /api/setup/status` |
| 기댓값 | `{"has_supervisor": true, "completed": true}` |

## T18: 프론트엔드 빌드 타입 검증

| 항목 | 내용 |
|------|------|
| 대상 | `pnpm build` (TypeScript + Vite) |
| 기댓값 | 빌드 성공, 타입 에러 없음 |
