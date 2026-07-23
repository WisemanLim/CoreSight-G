# 시험 결과 — Iteration 20: 트레이스(OTel) + trace-monitor Addon

- 일시: 2026-07-22
- 판정: **PASS** (자동 7/7 + 라이브 E2E)

## 자동 시험

```
uv run pytest test/impl/20/ -q → 7 passed
```

| ID | 결과 | 비고 |
|----|------|------|
| TC-20-01 비활성 no-op | PASS | otel_enabled=False → False |
| TC-20-02 초기화 실패 내성 | PASS | 예외 미전파 (앱 기동 지속) |
| TC-20-03 트레이스 요약 | PASS | 최신순, duration_ms/span_count/errors |
| TC-20-04 연결 실패 | PASS | JaegerError |
| TC-20-05 addon 규약 | PASS | tool↔executor 일치 |
| TC-20-06 배선 | PASS | trace_analysis → trace-monitor |
| TC-20-07 ZIP 3파일 | PASS | |

## 라이브 E2E (TC-20-08)

- 로더 `restored 4/4` (trace-monitor 포함), `/api/metrics/gpu` 트래픽 3회 후:
- Jaeger services: `['coresight-g-api']`
- addon `search_traces`: `GET /api/metrics/gpu` 36.11/35.04/52.33 ms · 11 spans
  (FastAPI 라우트 + httpx→Prometheus 하위 스팬 계측 확인)
- addon `/status`: instrumented_services=1

## 변경 요약

- 신규 의존성: opentelemetry-sdk/exporter-otlp-proto-http/instrumentation-{fastapi,httpx} (uv add)
- core: `app/core/tracing.py` (OTEL_ENABLED 가드·실패 내성), main.py 앱 생성 직후 계측,
  `app/services/jaeger.py` (조회 공통 서비스)
- compose: `jaeger` (all-in-one 1.62, UI 16686 / OTLP 4318)
- addon: `addon-agents/zip/trace-monitor/` + intent `trace_analysis` — **Addon-first 원칙 첫 적용**
  (core 라우터 없음, 조회·분석은 addon 만)
- env: OTEL_ENABLED/OTEL_EXPORTER_OTLP_ENDPOINT/JAEGER_URL (local=localhost, dev+=jaeger 컨테이너)
