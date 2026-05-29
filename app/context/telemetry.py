"""OpenTelemetry tracing setup.

ADK automatically emits spans for every agent turn, tool call, and LLM
request — no additional instrumentation is required beyond calling
configure_telemetry() once at application startup.

Cloud Run  → BatchSpanProcessor → Cloud Trace (GCP)
Local dev  → OTLP exporter when OTEL_EXPORTER_OTLP_ENDPOINT is set
             (e.g. Jaeger at http://localhost:4318), otherwise no-op
"""

from __future__ import annotations

import os
import structlog

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app import config

logger = structlog.get_logger(__name__)


def configure_telemetry() -> None:
    """Configure the global OpenTelemetry TracerProvider.

    Must be called before the FastAPI app or any ADK runners are created so
    that the provider is in place when the first span is emitted.
    """
    resource = Resource.create({SERVICE_NAME: "agentic-ai-engine"})

    if config.IS_CLOUD_RUN:
        _setup_cloud_trace(resource)
    else:
        _setup_local(resource)


def _setup_local(resource: Resource) -> None:
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    if otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint.rstrip('/')}/v1/traces")
            provider = TracerProvider(resource=resource)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(provider)
            logger.info("OpenTelemetry configured", exporter="otlp", endpoint=otlp_endpoint)
        except Exception:
            logger.warning("OpenTelemetry OTLP setup failed, falling back to no-op", exc_info=True)
            trace.set_tracer_provider(TracerProvider(resource=resource))
    else:
        trace.set_tracer_provider(TracerProvider(resource=resource))
        logger.debug("OpenTelemetry configured (no-op — set OTEL_EXPORTER_OTLP_ENDPOINT to export locally)")


def _setup_cloud_trace(resource: Resource) -> None:
    try:
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
        from opentelemetry.resourcedetector.gcp_resource_detector import (
            GoogleCloudResourceDetector,
        )

        # Merge static resource with Cloud Run metadata (service, revision, region …)
        gcp_resource = GoogleCloudResourceDetector().detect()
        merged_resource = resource.merge(gcp_resource)

        exporter = CloudTraceSpanExporter(project_id=config.GOOGLE_CLOUD_PROJECT)
        provider = TracerProvider(resource=merged_resource)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        logger.info(
            "OpenTelemetry configured",
            exporter="cloud_trace",
            project=config.GOOGLE_CLOUD_PROJECT,
        )
    except Exception:
        # Tracing must never prevent the app from starting.
        logger.warning("OpenTelemetry Cloud Trace setup failed, falling back to no-op", exc_info=True)
        trace.set_tracer_provider(TracerProvider(resource=resource))
