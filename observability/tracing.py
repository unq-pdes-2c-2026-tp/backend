from django.conf import settings
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_tracing():
    resource = Resource.create(
        {
            "service.name": "ctv-tracing",
            "service.version": "1.0.0",
        }
    )

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint=settings.OPENTELEMETRY_METRICS_ENDPOINT,
        insecure=True,
    )

    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)

    LoggingInstrumentor().instrument(
        set_logging_format=True,
    )
    DjangoInstrumentor().instrument()
