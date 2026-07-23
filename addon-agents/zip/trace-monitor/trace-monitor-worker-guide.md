# trace-monitor — 트레이스 분석 Addon Agent 가이드

## 역할
Jaeger(OTel) 에서 분산 트레이스를 조회해 수집 파이프라인 병목·오류를 분석하는 read-only 관제 Agent.
PRD "Addon-first 원칙"(Iteration 20~) 의 첫 적용 — 신규 관제 조회·분석 기능은 addon 으로 등록.

## 파일 규약
| 파일 | 용도 |
|------|------|
| `trace-monitor-app.py` | FastAPI router (`/api/addon/trace-monitor/*`) + `_TOOLS` + `TOOL_EXECUTORS` export |
| `trace-monitor-meta.json` | agent_type/capabilities (Agent Registry 등록용) |
| `trace-monitor.zip` | 업로드용 패키지 |

## 계측 (core 담당)
- `app/core/tracing.py` — `OTEL_ENABLED=true` 시 FastAPI 라우트 + httpx(Prometheus/Loki/LLM 호출) 계측
  → OTLP http(:4318) → Jaeger. 서비스명 `coresight-g-api`.
- Jaeger UI: `http://localhost:16686`

## 도구
| tool | 설명 |
|------|------|
| `list_services` | 계측 서비스 목록 |
| `search_traces` | 최근 트레이스 요약 (trace_id·지연 ms·스팬 수·오류 수), `min_duration_ms` 로 병목 탐지 |

## 환경변수
- `JAEGER_URL` (기본 `http://localhost:16686`), `OTEL_ENABLED`, `OTEL_EXPORTER_OTLP_ENDPOINT`

## 수동 점검
```bash
curl http://localhost:8100/api/addon/trace-monitor/status -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/trace-monitor/tools/search_traces \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"service":"coresight-g-api","minutes":30}'
```
