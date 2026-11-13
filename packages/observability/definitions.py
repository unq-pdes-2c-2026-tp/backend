from observability.metrics import meter

flights_api_request_duration = meter.create_histogram(
    "flights_api_request_duration",
    unit="s",
    description="Duracion de requests a la API de vuelos",
)
