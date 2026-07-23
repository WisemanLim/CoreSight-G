"""OpenTelemetry 계측 초기화 (PRD P1 — 자체 수집 파이프라인 관측).

OTEL_ENABLED=true 일 때만 활성. FastAPI 라우트 + httpx(Prometheus/Loki/LLM 호출) 계측
→ OTLP http 로 Jaeger(:4318) 전송. 조회·분석은 trace-monitor addon 담당 (Addon-first 원칙).
"""
import logging

from fastapi import FastAPI

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


def setup_tracing(app: FastAPI) -> bool:
    """계측 초기화. 비활성/실패 시 False (앱 기동은 계속)."""
    if not settings.otel_enabled:
        return False
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(
            resource=Resource.create({"service.name": settings.otel_service_name})
        )
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=f"{settings.otel_exporter_otlp_endpoint}/v1/traces")
            )
        )
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
        HTTPXClientInstrumentor().instrument(tracer_provider=provider)
        logger.info("[tracing] OTel 활성 → %s (service=%s)",
                    settings.otel_exporter_otlp_endpoint, settings.otel_service_name)
        return True
    except Exception as exc:  # noqa: BLE001 — 계측 실패가 서비스를 막으면 안 됨
        logger.warning("[tracing] OTel 초기화 실패(비활성으로 계속): %s", exc)
        return False
