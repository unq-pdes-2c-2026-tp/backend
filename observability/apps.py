from django.apps import AppConfig


class ObservabilityConfig(AppConfig):
    name = "observability"

    def ready(self):
        from observability.tracing import configure_tracing

        configure_tracing()
