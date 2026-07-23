# Phase 10 F23 Registry v2 시험 결과 (Iteration 9)

## 판정: PASS ✅

## 결과 요약

| TC | 시나리오 | 결과 |
|----|---------|------|
| TC-9-01 | Registry 목록 — v2 필드 포함 확인 | ✅ PASS |
| TC-9-02 | 외부 Agent 등록 (capabilities_json 포함) | ✅ PASS |
| TC-9-03 | capability search — verb 필터 | ✅ PASS |
| TC-9-04 | capability search — domain_prefix 필터 | ✅ PASS |
| TC-9-05 | capability search — agent_type 필터 | ✅ PASS |
| TC-9-06 | Agent Card 자동 생성 조회 | ✅ PASS |
| TC-9-07 | Agent Card 직접 업데이트 | ✅ PASS |
| TC-9-08 | Heartbeat 갱신 | ✅ PASS |
| TC-9-09 | Heartbeat → quarantined 상태 복구 | ✅ PASS |
| TC-9-10 | Health 조회 — 정상 상태 | ✅ PASS |
| TC-9-11 | Addon 업로드 시 capabilities DB 저장 | ✅ PASS |
| TC-9-12 | 무효 Agent Card JSON → 400 | ✅ PASS |

**총 12개 / 12 PASS, 0 FAIL**  
실행 시간: 4.57s

## 실행 환경

- Python 3.13.12
- pytest 9.1.1 + pytest-asyncio 1.4.0
- SQLite (로컬 테스트 DB)

## 확인된 구현 사항

- `tbl_agent_registry` v2 컬럼 마이그레이션: agent_type, capabilities_json, agent_card_json, lifecycle_state, health_score, last_heartbeat_at, lease_expires_at
- `tbl_addon_agent_capabilities` 신규 테이블 자동 생성
- capability 기반 검색 (verb OR, domain_prefix, agent_type 필터)
- Agent Card 자동 생성 (identity + capabilities + endpoints 구조)
- Agent Card 직접 업데이트 및 조회
- Heartbeat → lease 연장 + quarantined 자동 복구
- 실시간 헬스 조회 (health_dot: green/orange/red, lease_expired 계산)
- Addon 업로드 시 meta_json capabilities → tbl_addon_agent_capabilities 자동 저장
