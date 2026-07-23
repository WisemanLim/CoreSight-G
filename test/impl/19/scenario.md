# 시험 시나리오 — Iteration 19: 로그 수집·검색 (PRD §3 P1) + 로그 분석 Agent

## 범위
- Loki 3.4 (compose `loki`, :3100, retention 15d) + mock 로그 생성기(syslog/dmesg/bmc)
- `app/services/loki.py` (search/labels/build_logql) + `GET /api/logs/{search,labels}`
- `addon-agents/zip/log-analyzer/` (tools: search_logs, recent_errors) + intent `log_analysis`

## 테스트 케이스

| ID | 내용 | 방법 | 기대 결과 |
|----|------|------|----------|
| TC-19-01 | build_logql 조립 | 단위 | job/level/keyword 조합별 LogQL |
| TC-19-02 | search 평탄화·정렬 | _get 모킹 | 스트림 병합, ts 내림차순, limit |
| TC-19-03 | Loki 연결 실패 | httpx 오류 모킹 | LokiError |
| TC-19-04 | /api/logs/* 미인증 | 토큰 없이 | 401/403 |
| TC-19-05 | /api/logs/search 정상 | 서비스 모킹 + 인증 오버라이드 | 200 + entries |
| TC-19-06 | /api/logs/search Loki 다운 | LokiError 모킹 | 503 |
| TC-19-07 | log-analyzer 모듈 규약 | importlib 로드 | router + tool↔executor 일치 |
| TC-19-08 | orchestrator 배선 | import 검사 | log_analysis → addon_key log-analyzer |
| TC-19-09 | ZIP 패키지 | zipfile | 3파일 |
| TC-19-10 | (라이브) E2E | 생성기→Loki→API | labels [bmc,dmesg,syslog], keyword 검색 히트 |

## 실행
```bash
uv run pytest test/impl/19/ -v
```
