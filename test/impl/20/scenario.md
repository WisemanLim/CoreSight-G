# 시험 시나리오 — Iteration 20: 트레이스(OTel) + trace-monitor Addon (PRD §3 P1, Addon-first 첫 적용)

## 범위
- OTel 계측: `app/core/tracing.py` (OTEL_ENABLED 가드, FastAPI+httpx, OTLP→Jaeger:4318)
- compose `jaeger` (all-in-one 1.62, UI 16686)
- `app/services/jaeger.py` (services/search_traces 요약)
- `addon-agents/zip/trace-monitor/` (tools: list_services·search_traces) + intent `trace_analysis`

## 테스트 케이스

| ID | 내용 | 방법 | 기대 결과 |
|----|------|------|----------|
| TC-20-01 | tracing 비활성 no-op | otel_enabled=False | setup_tracing → False, 예외 없음 |
| TC-20-02 | tracing 실패 내성 | exporter 초기화 예외 모킹 | False 반환, 앱 기동 지속 |
| TC-20-03 | search_traces 요약 변환 | _get 모킹 | trace_id/duration_ms/span_count/errors, 최신순 |
| TC-20-04 | Jaeger 연결 실패 | httpx 오류 모킹 | JaegerError |
| TC-20-05 | addon 모듈 규약 | importlib 로드 | router + tool↔executor 일치 |
| TC-20-06 | orchestrator 배선 | import 검사 | trace_analysis → trace-monitor |
| TC-20-07 | ZIP 패키지 | zipfile | 3파일 |
| TC-20-08 | (라이브) E2E | 트래픽 → Jaeger → addon | services=[coresight-g-api], 트레이스 요약 반환 |

## 실행
```bash
uv run pytest test/impl/20/ -v
```
