# 시험 시나리오 — Iteration 22: Addon-first 정합 보완 (요청사항 재확인 반영)

## 배경 (사용자 재확인 요청 2건)
1. P1 로그·트레이스는 **Addon 에이전트로 구현**되어야 함
   → 점검 결과 트레이스(20차)는 준수, **로그(19차)는 core `/api/logs/*` 라우터가 존재(위반)**.
2. Addon 에이전트 활성화 시 대시보드 반영 + 위젯 미제공 시 예외처리
   → 점검 결과 위젯이 addon `is_active` 만 확인, **에이전트 관리의 관제 Agent 토글(agent_config)과 비연동(누락)**.

## 수정 범위
- core `app/routers/router_logs.py` 삭제 + main.py 배선 제거 — 로그 조회는 log-analyzer addon 전용.
  (`app/services/loki.py` 는 addon 이 import 하는 공용 클라이언트로 유지 — prometheus/jaeger 와 동일 패턴)
- 대시보드 위젯 필터 이중화: addon `is_active` **AND** `agent_config`(관제 Agent 토글) 활성.
  addon_key→config_key 매핑(`ADDON_CONFIG_KEY`) + 미등록 addon 은 `-`→`_` 규약.
- 예외처리 유지: /status 미제공·다운 addon 은 per-addon try/catch 로 스킵.

## 테스트 케이스

| ID | 내용 | 기대 결과 |
|----|------|----------|
| TC-22-01 | core /api/logs/* 부재 | 404 (test_phase19 개정판에 회귀 시험 포함) |
| TC-22-02 | addon search_logs 대체 경로 | 라이브 count>0 |
| TC-22-03 | 위젯 토글 연동 | log_analysis OFF → 위젯 필터 제외 (build + 로직) |
| TC-22-04 | 프론트 빌드 | tsc + vite 오류 없음 |
| TC-22-05 | 회귀 | impl/14~20 전체 PASS |
