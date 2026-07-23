# 시험 결과 — Iteration 21: 대시보드 ↔ 관제 Agent 활성화 연동

- 일시: 2026-07-22
- 판정: **PASS**

| ID | 결과 | 비고 |
|----|------|------|
| TC-21-01 | PASS | `pnpm build` 1.11s (tsc 포함) |
| TC-21-02 | PASS | log-analyzer `{"error_count_1h":0}`, trace-monitor `{"instrumented_services":2,...}` — 위젯 카드 데이터 확인 |
| TC-21-03 | PASS | PATCH 후 `hardware is_enabled=0` → 대시보드 load() 가 HW 섹션 숨김·조회 스킵. 복원 완료 |
| TC-21-04 | PASS(설계) | addon 별 개별 try/catch → null 필터. 404/503/네트워크 모두 스킵 경로 동일 |
| TC-21-05 | PASS | /dashboard 200 — "관제 Agent 위젯" 섹션에 로그 분석·트레이스 분석 카드 렌더 |

## 구현 (front/src/pages/dashboard/DashboardPage.tsx)

- `listAgentConfigs()` → `enabled` 맵: GPU 섹션(`gpu_monitoring`)·HW 섹션(`hardware`) 조건부 렌더
  + 비활성 시 해당 메트릭 조회 자체를 스킵(불필요 트래픽 제거).
  조회 실패 시 기본값 전체 표시(대시보드 가용성 우선).
- `listAddonAgents()` → 활성 addon 별 `GET /api/addon/<key>/status` 위젯 카드
  (상위 프리미티브 필드 최대 6개). 전용 섹션 보유 addon(gpu-monitor/hw-monitor) 제외.
- **위젯 규약**: 새 Addon 에이전트는 `/status` 엔드포인트만 구현하면 활성화 시 대시보드 자동 반영.
  미구현 addon 은 예외처리로 자동 스킵 — 프론트 수정 불필요.
