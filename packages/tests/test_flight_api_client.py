from unittest.mock import patch, MagicMock
from urllib.parse import urljoin

from django.test import override_settings

from packages.flight_api_client import FlightAPIClient


@override_settings(FLIGHTS_API_URL="http://test.com")
def test_buy_flight_payload():
    mock_session = MagicMock()
    with patch("packages.flight_api_client.Session", return_value=mock_session):
        mock_session.post = MagicMock()
        client = FlightAPIClient()
        client.buy_flight(1, "pepe", "pepe@mail.com")

        mock_session.post.assert_called_with(
            urljoin("http://test.com", "vender/"),
            json={
                "vuelo": 1,
                "nombre_pasajero": "pepe",
                "email_pasajero": "pepe@mail.com",
            },
            timeout=5,
        )
