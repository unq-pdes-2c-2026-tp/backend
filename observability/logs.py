import logging
from django.conf import settings

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.instrumentation.logging.handler import LoggingHandler
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource


def configure_logging():
    logger_provider = LoggerProvider(
        resource=Resource.create(
            {
                "service.name": "ctv",
            }
        )
    )

    exporter = OTLPLogExporter(
        endpoint=settings.OPENTELEMETRY_METRICS_ENDPOINT,
        insecure=True,
    )

    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    set_logger_provider(logger_provider)

    handler = LoggingHandler(
        level=logging.INFO,
        logger_provider=logger_provider,
    )

    logging.getLogger().addHandler(handler)
