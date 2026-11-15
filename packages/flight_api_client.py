import logging
from urllib.parse import urljoin

from requests import Session
from django.conf import settings

from packages.observability.decorators import measure_time
from packages.observability.definitions import flights_api_request_duration


logger = logging.getLogger(__name__)


class FlightAPIClient:
    def __init__(self):
        self._session = None
        self._timeout = 5

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = Session()

        return self._session

    @measure_time(flights_api_request_duration)
    def get_flights(self, search: str):
        logger.info(f"get_flights: {search}")
        params = {"search": search} if search else {}
        response = self.session.get(
            urljoin(settings.FLIGHTS_API_URL, "vuelos/"),
            params=params,
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()

    @measure_time(flights_api_request_duration)
    def get_flight(self, flight_id: int):
        logger.info("get_flight")
        response = self.session.get(
            urljoin(settings.FLIGHTS_API_URL, f"vuelos/{flight_id}/"),
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()

    @measure_time(flights_api_request_duration)
    def buy_flight(self, flight_id, user_name, user_email):
        logger.info(f"buy_flight: {flight_id} {user_name} {user_email}")
        response = self.session.post(
            urljoin(settings.FLIGHTS_API_URL, "vender/"),
            json={
                "vuelo": flight_id,
                "nombre_pasajero": user_name,
                "email_pasajero": user_email,
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
