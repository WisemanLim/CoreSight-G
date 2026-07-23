# 시험 시나리오 — Iteration 23: P1 Agent 를 ADDON 에이전트로 등록·관리 (재확인 요청 반영)

## 배경
에이전트 관리 화면에서 P1(로그 분석·트레이스 분석)이 내장 "관제 AGENT" 섹션에 표시됨(위반).
원인: 시드가 `is_builtin=1` + `tbl_agent_config` 행 등록.

## 수정 범위
- 시드(sqlite/pg): log-analyzer·trace-monitor `is_builtin=0`, agent_config 행(log_analysis/trace_analysis) 제거+정리 DELETE
- orchestrator `_disabled_agents()`: `tbl_addon_agents.is_active=0` 를 addon_key→intent 역매핑으로 반영
  (agent_config 행 없는 Addon 에이전트의 intent 게이팅)
- 대시보드 위젯: config 행 부재 시 addon `is_active` 단독 게이팅(기존 필터가 자동 처리)
- GPU/HW(P0)는 기존 설계 유지(내장 관제 AGENT + 전용 대시보드 섹션)

## 테스트 케이스

| ID | 내용 | 기대 결과 |
|----|------|----------|
| TC-23-01 | agent_config 목록 | general/chat/gpu_monitoring/hardware 만 (P1 없음) |
| TC-23-02 | addon 목록 | log-analyzer·trace-monitor `is_builtin=0` → ADDON 에이전트 섹션 표시 |
| TC-23-03 | addon 토글 게이팅 | toggle OFF → `/api/addon/log-analyzer/*` 404, ON → 200 |
| TC-23-04 | intent 게이팅 (단위) | addon is_active=0 → `_disabled_agents()` 에 해당 intent 포함 |
| TC-23-05 | 회귀 | impl/14~20 PASS |
