# 시험 결과 — Iteration 22: Addon-first 정합 보완

- 일시: 2026-07-22
- 판정: **PASS** (회귀 42/42 + 라이브)

| ID | 결과 | 비고 |
|----|------|------|
| TC-22-01 core /api/logs/* 부재 | PASS | 라이브 404 + test_phase19 개정판 `test_core_logs_router_removed` |
| TC-22-02 addon 대체 경로 | PASS | `POST /api/addon/log-analyzer/tools/search_logs` count=2 |
| TC-22-03 위젯 토글 연동 | PASS | 필터 = addon `is_active` AND `agent_config` 활성 (`ADDON_CONFIG_KEY` 매핑 + `-`→`_` 규약) |
| TC-22-04 프론트 빌드 | PASS | 1.06s |
| TC-22-05 회귀 | PASS | impl/14~20 42/42, ruff clean |

## 수정 내역

1. **로그 Addon-first 위반 해소**: core `app/routers/router_logs.py` 삭제, main.py 배선 제거.
   로그 조회·검색은 log-analyzer addon(`/api/addon/log-analyzer/*`) 전용.
   `app/services/loki.py` 는 addon 이 사용하는 공용 클라이언트로 유지 (prometheus/jaeger 동일 패턴).
   test_phase19 TC-04/05/06 을 addon 기반으로 개정(개정 사유 주석).
2. **위젯 ↔ 관제 Agent 토글 연동 누락 보완**: 대시보드 addon 위젯이 addon `is_active` 만 확인하던 것을
   에이전트 관리의 관제 Agent 토글(tbl_agent_config)과 AND 조건으로 이중화.
   매핑: gpu-monitor→gpu_monitoring, hw-monitor→hardware, log-analyzer→log_analysis,
   trace-monitor→trace_analysis (신규 addon 은 `-`→`_` 자동 유도).
3. 예외처리(위젯 미제공 addon 스킵)는 21차 구현 유지 — per-addon try/catch.
