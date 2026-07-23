# 시험 시나리오 — Iteration 21: 대시보드 ↔ 관제 Agent 활성화 연동 + Addon 위젯 규약

## 범위
- 대시보드 섹션을 관제 Agent 활성화 상태와 연동:
  GPU 섹션 = `gpu_monitoring`, HW 섹션 = `hardware` (비활성 시 숨김 + 해당 조회 스킵)
- 활성 Addon 에이전트 위젯 자동 반영: `GET /api/addon/<key>/status` 규약 —
  응답 상위 프리미티브 필드를 카드로 표시 (gpu-monitor/hw-monitor 는 전용 섹션이라 제외)
- **예외처리 필수**: /status 미제공(404)·백엔드 다운(503)·네트워크 오류 addon 은
  오류 배너 없이 위젯에서 스킵. agent-config 조회 실패 시 기본값(전체 표시) 유지

## 테스트 케이스

| ID | 내용 | 방법 | 기대 결과 |
|----|------|------|----------|
| TC-21-01 | 타입·빌드 | `pnpm build` (tsc) | 오류 없음 |
| TC-21-02 | (라이브) 위젯 소스 | addon /status | log-analyzer `{error_count_1h}`, trace-monitor `{instrumented_services}` |
| TC-21-03 | (라이브) 토글 반영 | PATCH agent-config hardware=false → 목록 확인 → 복원 | is_enabled 0 반영, 대시보드 폴링 시 HW 섹션 숨김 |
| TC-21-04 | (설계) 미제공 addon | /status 없는 addon 활성 | 위젯 스킵, 콘솔 오류·배너 없음 (per-addon try/catch) |
| TC-21-05 | (수동, UI) 대시보드 | 브라우저 | 관제 Agent 위젯 섹션에 로그/트레이스 카드 표시 |
