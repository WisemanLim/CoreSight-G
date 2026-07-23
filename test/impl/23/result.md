# 시험 결과 — Iteration 23: P1 Agent 의 ADDON 에이전트 등록·관리

- 일시: 2026-07-22
- 판정: **PASS** (자동 3/3 + 회귀 42/42 + 라이브)

| ID | 결과 | 비고 |
|----|------|------|
| TC-23-01 | PASS | agent-config 목록 = general·chat·gpu_monitoring·hardware (P1 제거) |
| TC-23-02 | PASS | addon 목록: log-analyzer/trace-monitor `is_builtin=0, is_active=1` → 에이전트 관리 "ADDON 에이전트" 섹션 표시 |
| TC-23-03 | PASS | toggle OFF → `/api/addon/log-analyzer/tools` 404(미들웨어 차단) → ON → 200 |
| TC-23-04 | PASS | addon is_active=0 → `_disabled_agents()` 가 log_analysis/trace_analysis intent 차단 |
| TC-23-05 | PASS | impl/14~20 42/42, ruff clean |

## 수정 내역

- 시드(sqlite/pg): P1 addon `is_builtin=0`, `tbl_agent_config` 의 log_analysis/trace_analysis
  행 제거 + 정리 DELETE(기존 DB 멱등 정리). local.db 즉시 반영.
- orchestrator `_disabled_agents()`: `tbl_addon_agents.is_active=0` 를 `_AGENT_MAP` 의
  addon_key→intent 역매핑으로 비활성 intent 에 포함 — ADDON 토글만으로 채팅 라우팅까지 차단.
- 대시보드 위젯: agent_config 행 부재 시 addon `is_active` 단독 게이팅(기존 필터 자동 처리),
  위젯 미제공 addon 예외처리 유지.
- 관리 체계 확정: **P0(GPU/HW) = 내장 관제 AGENT**(agent_config 토글 + 전용 대시보드 섹션),
  **P1~(로그/트레이스/향후) = ADDON 에이전트**(is_active 토글 + /status 위젯).
