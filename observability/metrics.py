from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource

from django.conf import settings


def configure_metrics():
    resource = Resource.create(
        {
            "service.name": "ctv-metrics",
            "service.version": "1.0.0",
        }
    )

    exporter = OTLPMetricExporter(
        endpoint=settings.OPENTELEMETRY_METRICS_ENDPOINT,
        insecure=True,
    )

    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=10000,
    )

    provider = MeterProvider(
        resource=resource,
        metric_readers=[reader],
    )

    metrics.set_meter_provider(provider)

    return metrics.get_meter("ctv-metrics")


meter = configure_metrics()
