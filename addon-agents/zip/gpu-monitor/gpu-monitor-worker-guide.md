# gpu-monitor — GPU 관제 Addon Agent 가이드

## 역할
Prometheus(DCGM 메트릭)에서 GPU 상태를 조회하는 read-only 관제 Agent.
조치 실행(노드 격리·재시작)은 범위 밖 — 권고만 제시.

## 파일 규약
| 파일 | 용도 |
|------|------|
| `gpu-monitor-app.py` | FastAPI router (`/api/addon/gpu-monitor/*`) + `_TOOLS` + `TOOL_EXECUTORS` export |
| `gpu-monitor-meta.json` | agent_type/capabilities (Agent Registry 등록용) |
| `gpu-monitor.zip` | 업로드용 패키지 (`에이전트 관리 → Addon 등록`) |

## Domain Agent 연동 (core AddonToolAgent 규약)
core 의 `app/agents/addon_tool_agent.py` 가 로드된 addon 모듈(`sys.modules["addon_gpu-monitor"]`)에서
`_TOOLS`(Anthropic tool_use 스키마)·`TOOL_EXECUTORS`(async 실행기)·`SYSTEM_PROMPT` 를 읽어
Orchestrator intent `gpu_monitoring` 의 tool_use 루프에 사용한다.

## 도구
| tool | 설명 |
|------|------|
| `get_gpu_snapshot` | GPU 별 utilization/VRAM/온도/전력/XID/ECC 스냅샷 |
| `get_active_alerts` | 활성(firing/pending) 알람 목록 |
| `query_promql` | PromQL instant query 직접 실행 |

## 환경변수
- `PROMETHEUS_URL` (기본 `http://localhost:9090`)

## 수동 점검
```bash
curl http://localhost:8100/api/addon/gpu-monitor/tools -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/gpu-monitor/tools/get_gpu_snapshot \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
curl http://localhost:8100/api/addon/gpu-monitor/status -H "Authorization: Bearer $TOKEN"
```
