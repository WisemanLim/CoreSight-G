# 시험 결과 — Iteration 19: 로그 수집·검색 (P1) + 로그 분석 Agent

- 일시: 2026-07-22
- 판정: **PASS** (자동 9/9 + 회귀 14~18차 포함 35/35 + 라이브 E2E)

## 자동 시험 (pytest)

```
uv run pytest test/impl/19/ -v → 9 passed
```

| ID | 결과 | 비고 |
|----|------|------|
| TC-19-01 build_logql | PASS | job/level/keyword 조합 + 따옴표 이스케이프 |
| TC-19-02 search 평탄화·정렬 | PASS | 스트림 병합, ts 내림차순, limit |
| TC-19-03 연결 실패 | PASS | LokiError |
| TC-19-04 미인증 | PASS | search/labels 401/403 |
| TC-19-05 search 200 | PASS | 서비스 모킹 |
| TC-19-06 Loki 다운 503 | PASS | |
| TC-19-07 addon 모듈 규약 | PASS | tool↔executor 일치 |
| TC-19-08 orchestrator 배선 | PASS | log_analysis → log-analyzer |
| TC-19-09 ZIP 3파일 | PASS | |

## 라이브 E2E (TC-19-10)

- 로더: `[addon_loader] restored 3/3 addon(s)` — log-analyzer 마운트
- `GET /api/logs/labels` → `["bmc","dmesg","syslog"]`
- `GET /api/logs/search?job=dmesg` → dmesg 라인 반환
- `GET /api/logs/search?keyword=nvidia` → `{job=~".+"} |~ "(?i)nvidia"` 히트 확인
  (초기 0건은 생성기 로그 축적 전 타이밍 — 20s 후 정상)
- addon 도구 `search_logs`/`recent_errors`/`/status` 동작 (정상 모드 error_count_1h=0)
- 이상 로그 재현: `MOCK_ANOMALY=1` 로 log-generator 재기동 시 Xid/RAID DEGRADED/ECC error 로그 주입

## 변경 요약

- compose: `loki`(grafana/loki:3.4.2, :3100, retention 15d/tsdb/파일시스템) + `log-generator`(stdlib push)
- 백엔드: `app/services/loki.py`, `GET /api/logs/{search,labels}` (read-only, 인증)
- addon: `addon-agents/zip/log-analyzer/` (search_logs·recent_errors) + intent `log_analysis`
- 시드: tbl_addon_agents(log-analyzer) + tbl_agent_config(log_analysis, 관제 Agent 그룹)
- env: `LOKI_URL`/`LOKI_PORT` (local=localhost, dev+=http://loki:3100)

## 운영 전환 메모

- `log-generator` 제거 후 실 노드에 Promtail/Grafana Alloy 배포 → Loki push (라벨 규약:
  `job=syslog|dmesg|bmc`, `Hostname=<node>`, `level=info|warning|error`).
