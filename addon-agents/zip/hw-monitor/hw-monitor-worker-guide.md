# hw-monitor — 서버 하드웨어 관제 Addon Agent 가이드

## 역할
Prometheus 에서 서버 하드웨어(CPU/메모리/RAID/PSU/센서) 상태를 조회하는 read-only 관제 Agent.
조치 실행은 범위 밖 — 권고만 제시.

## 파일 규약
| 파일 | 용도 |
|------|------|
| `hw-monitor-app.py` | FastAPI router (`/api/addon/hw-monitor/*`) + `_TOOLS` + `TOOL_EXECUTORS` export |
| `hw-monitor-meta.json` | agent_type/capabilities (Agent Registry 등록용) |
| `hw-monitor.zip` | 업로드용 패키지 |

## Domain Agent 연동 (core AddonToolAgent 규약)
core 의 `app/agents/addon_tool_agent.py` 가 로드된 addon 모듈(`sys.modules["addon_hw-monitor"]`)에서
`_TOOLS`·`TOOL_EXECUTORS`·`SYSTEM_PROMPT` 를 읽어 Orchestrator intent `hardware` 의 tool_use 루프에 사용한다.

## 도구
| tool | 설명 |
|------|------|
| `get_hardware_snapshot` | 노드 별 CPU/메모리/RAID/PSU/흡기온도 스냅샷 |
| `get_active_alerts` | 활성(firing/pending) 알람 목록 |
| `query_promql` | PromQL instant query 직접 실행 |

## 환경변수
- `PROMETHEUS_URL` (기본 `http://localhost:9090`)

## 수동 점검
```bash
curl http://localhost:8100/api/addon/hw-monitor/tools -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/hw-monitor/tools/get_hardware_snapshot \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
curl http://localhost:8100/api/addon/hw-monitor/status -H "Authorization: Bearer $TOKEN"
```
