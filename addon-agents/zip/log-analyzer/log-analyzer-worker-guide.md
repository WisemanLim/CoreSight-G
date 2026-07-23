# log-analyzer — 로그 분석 Addon Agent 가이드

## 역할
Loki 에서 시스템(syslog)/커널(dmesg)/BMC 로그를 검색·분석하는 read-only 관제 Agent (PRD P1).

## 파일 규약
| 파일 | 용도 |
|------|------|
| `log-analyzer-app.py` | FastAPI router (`/api/addon/log-analyzer/*`) + `_TOOLS` + `TOOL_EXECUTORS` export |
| `log-analyzer-meta.json` | agent_type/capabilities (Agent Registry 등록용) |
| `log-analyzer.zip` | 업로드용 패키지 |

## Domain Agent 연동
core `AddonToolAgent` 가 `sys.modules["addon_log-analyzer"]` 에서 `_TOOLS`·`TOOL_EXECUTORS`·
`SYSTEM_PROMPT` 를 읽어 Orchestrator intent `log_analysis` 의 tool_use 루프에 사용.

## 도구
| tool | 설명 |
|------|------|
| `search_logs` | job(syslog/dmesg/bmc)·keyword·level·minutes 로 로그 검색 |
| `recent_errors` | 최근 error 레벨 로그 전 소스 조회 (기본 60분) |

## 환경변수
- `LOKI_URL` (기본 `http://localhost:3100`)

## 수동 점검
```bash
curl http://localhost:8100/api/addon/log-analyzer/tools -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/log-analyzer/tools/search_logs \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"job":"dmesg","keyword":"Xid","minutes":60}'
curl http://localhost:8100/api/addon/log-analyzer/status -H "Authorization: Bearer $TOKEN"
```
