# 시험 시나리오 — Iteration 17: 화면 없는 addon 의 사이드바 메뉴 노출 버그 수정

## 배경
gpu-monitor/hw-monitor 는 API 전용(`has_front=0`) addon 인데 좌측 내비게이션에
`/addon/<key>` 메뉴가 노출됨 — 클릭 시 빈 채팅 placeholder 화면.

## 원인
`AppLayout.tsx` `refreshAgents()` 가 `is_active` 만 필터하고 `has_front` 를 확인하지 않음.

## 테스트 케이스

| ID | 내용 | 방법 | 기대 결과 |
|----|------|------|----------|
| TC-17-01 | API 플래그 확인 | `GET /api/addon-agents/` | gpu-monitor/hw-monitor: has_front=0, is_active=1 |
| TC-17-02 | 타입·빌드 검증 | `pnpm build` (tsc --noEmit) | 오류 없음 |
| TC-17-03 | (수동, UI) 사이드바 | 브라우저 새로고침 | GPU 모니터링/하드웨어 Agent 메뉴 미노출. 대시보드·AI 어시스턴트·에이전트·사용자 메뉴 정상 |
| TC-17-04 | (수동, UI) has_front=1 addon 회귀 | front 포함 addon 업로드 시 | 메뉴 정상 노출 (필터 조건 `is_active && has_front`) |
