# Phase 10 F23 Registry v2 시험 시나리오 (Iteration 9)

## 목적

F23 Agent Registry v2 구현 검증:
- tbl_agent_registry v2 컬럼 (agent_type, capabilities_json, lifecycle_state, health_score)
- tbl_addon_agent_capabilities 테이블 생성 및 addon 업로드 시 자동 저장
- POST /api/agent-registry/search — capability 기반 검색
- GET  /api/agent-registry/{key}/card — Agent Card 자동 생성
- PUT  /api/agent-registry/{key}/card — Agent Card 업데이트
- POST /api/agent-registry/{key}/heartbeat — Heartbeat 갱신 + lifecycle_state 복구
- GET  /api/agent-registry/{key}/health — 실시간 헬스 상태

## 테스트 케이스

| TC | 시나리오 | 예상 결과 |
|----|---------|---------|
| TC-9-01 | Registry 목록 — v2 필드 포함 확인 | agent_type, lifecycle_state, health_dot 필드 존재 |
| TC-9-02 | 외부 Agent 등록 (capabilities_json 포함) | 201, agent_key 반환 |
| TC-9-03 | capability search — verb 필터 | 해당 verb 보유 Agent만 반환 |
| TC-9-04 | capability search — domain_prefix 필터 | 해당 domain으로 시작하는 Agent만 |
| TC-9-05 | capability search — agent_type 필터 | 해당 유형 Agent만 반환 |
| TC-9-06 | Agent Card 자동 생성 조회 | capabilities + endpoints 포함된 Card 반환 |
| TC-9-07 | Agent Card 직접 업데이트 | 200, 이후 조회 시 업데이트된 JSON 반환 |
| TC-9-08 | Heartbeat 갱신 | 200, last_heartbeat_at 갱신, lifecycle_state=active |
| TC-9-09 | Heartbeat → quarantined 상태 복구 | heartbeat 후 lifecycle_state=active |
| TC-9-10 | Health 조회 — 정상 상태 | health_dot=green, lease_expired=false |
| TC-9-11 | Addon 업로드 시 capabilities DB 저장 | tbl_addon_agent_capabilities에 행 존재 |
| TC-9-12 | 무효 Agent Card JSON → 400 | 400 반환 |
