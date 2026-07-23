# 시험 결과 — Iteration 17: 화면 없는 addon 사이드바 노출 버그 수정

- 일시: 2026-07-22
- 판정: **PASS**

| ID | 결과 | 비고 |
|----|------|------|
| TC-17-01 | PASS | API 응답 `[('gpu-monitor', 0, 1), ('hw-monitor', 0, 1)]` — has_front=0 확인 |
| TC-17-02 | PASS | `pnpm build` 1.10s, tsc 오류 없음 |
| TC-17-03 | PASS | 필터 `is_active && has_front` 적용 — API 전용 addon 메뉴 미노출 (vite HMR 반영) |
| TC-17-04 | PASS(설계) | has_front=1 인 addon 만 노출되도록 조건 유지 — 업로드 회귀는 향후 front 포함 addon 등록 시 확인 |

## 수정

- [front/src/components/layout/AppLayout.tsx](../../front/src/components/layout/AppLayout.tsx)
  `refreshAgents()`: `.filter((a) => a.is_active && a.has_front)` — 1라인 수정.
- 에이전트 관리(`/agents`) 화면·채팅 intent 라우팅은 영향 없음
  (관제 Agent 는 tbl_agent_config 기반 "관제 AGENT" 섹션·orchestrator 매핑으로 동작).
