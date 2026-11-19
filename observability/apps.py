from django.apps import AppConfig


class ObservabilityConfig(AppConfig):
    name = "observability"

    def ready(self):
        from observability.tracing import configure_tracing
        from observability.logs import configure_logging

        configure_tracing()
        configure_logging()
