# Phase 12 F25 Orchestrator 고도화 시험 시나리오 (Iteration 11)

## 목적

F25 Orchestrator 고도화 구현 검증:
- F25-1 capability 기반 Registry 동적 라우팅 (`registry_dynamic_routing` 설정)
- F25-2 Reviewer Gate 내장 (`reviewer_gate_enabled` 설정)
- F25-3 HITL 게이트 (`hitl_gate_enabled` 설정)
- F25-4 SSE 신규 이벤트 (`registry_miss`, `review_gate`, `hitl_pending`)
- 기본 동작: 모든 게이트 off → v1.4 호환 유지

## 테스트 케이스

| TC | 시나리오 | 예상 결과 |
|----|---------|---------|
| TC-11-01 | 기본값: 모든 게이트 off → SSE done 이벤트 정상 반환 | 200, done 이벤트 포함 |
| TC-11-02 | registry_dynamic_routing=true + 미지정 intent → registry_miss 이벤트 | SSE에 registry_miss 이벤트 포함 |
| TC-11-03 | registry_dynamic_routing=false → registry_miss 이벤트 없음 | SSE에 registry_miss 없음 |
| TC-11-04 | hitl_gate_enabled=true + delete intent + HITL addon 존재 → hitl_pending | SSE에 hitl_pending 이벤트 포함 |
| TC-11-05 | hitl_gate_enabled=true + delete intent + HITL addon 없음 → 정상 실행 | hitl_pending 없음, done 이벤트 |
| TC-11-06 | hitl_gate_enabled=false + delete intent → 정상 실행 (게이트 미작동) | done 이벤트 |
| TC-11-07 | reviewer_gate_enabled=true + reviewer addon 없음 → review_gate 이벤트 없음 | review_gate 없음, done |
| TC-11-08 | _get_setting_bool → true 파싱 정확성 | "true"/"1"/"yes" → True |
| TC-11-09 | _registry_find_by_verb — capabilities DB 조회 정상 | list 반환 |
| TC-11-10 | _find_agent_by_type — agent_type 필터 정상 | dict or None |
| TC-11-11 | run() — 기본 동작 (Anthropic key 없음 → Ollama fallback) | 문자열 응답 반환 |
| TC-11-12 | SSE stream 헤더: Content-Type text/event-stream 확인 | 헤더 정상 |
