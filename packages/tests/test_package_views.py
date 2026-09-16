import pytest
from decimal import Decimal
from django.urls import reverse
from unittest.mock import Mock, patch
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN

from packages.models import Agency, City, Package
from packages.tests.factories import HotelFactory
from test_utils.views import post
from users.constants import UserType
from users.models import User


@pytest.mark.django_db
@patch("packages.serializers.requests.get")
def test_agency_can_create_package(mock_get):
    mock_get.side_effect = [
        Mock(status_code=200, json=lambda: {"origen": "Buenos Aires", "destino": "Bariloche"}),
        Mock(status_code=200, json=lambda: {"origen": "Bariloche", "destino": "Buenos Aires"}),
    ]
    agency = Agency.objects.create(name="Andes Travel")
    user = User.objects.create_user(
        email="agency@mail.com",
        password="123",
        name="Agencia",
        user_type=UserType.AGENCY,
        agency=agency,
    )
    hotel = HotelFactory()
    origin = City.objects.create(name="Buenos Aires")
    data = {
        "hotel": hotel.id,
        "origin": origin.id,
        "outbound_flight_id": 10,
        "outbound_flight_date": "2026-10-10T09:00:00Z",
        "return_flight_id": 11,
        "return_flight_date": "2026-10-17T18:00:00Z",
        "name": "Escapada de prueba",
        "description": "Una escapada breve.",
        "price": "125000.50",
    }

    response = post(reverse("package-list"), data, user=user)

    assert response.status_code == HTTP_201_CREATED
    package = Package.objects.get(name="Escapada de prueba")
    assert package.agency == agency
    assert package.hotel == hotel
    assert package.price == Decimal("125000.50")
    assert response.json()["hotel_photo"] is None


@pytest.mark.django_db
@patch("packages.serializers.requests.get")
def test_package_requires_return_flight_to_reverse_route(mock_get):
    mock_get.side_effect = [
        Mock(status_code=200, json=lambda: {"origen": "Buenos Aires", "destino": "Bariloche"}),
        Mock(status_code=200, json=lambda: {"origen": "Mendoza", "destino": "Buenos Aires"}),
    ]
    agency = Agency.objects.create(name="Andes Travel")
    user = User.objects.create_user(
        email="agency-route@mail.com",
        password="123",
        name="Agencia",
        user_type=UserType.AGENCY,
        agency=agency,
    )
    hotel = HotelFactory()
    origin = City.objects.create(name="Buenos Aires")
    data = {
        "hotel": hotel.id,
        "origin": origin.id,
        "outbound_flight_id": 10,
        "outbound_flight_date": "2026-10-10T09:00:00Z",
        "return_flight_id": 11,
        "return_flight_date": "2026-10-17T18:00:00Z",
        "name": "Ruta inválida",
        "description": "",
        "price": "100.00",
    }

    response = post(reverse("package-list"), data, user=user)

    assert response.status_code == 400
    assert "return_flight_id" in response.json()


@pytest.mark.django_db
def test_non_agency_cannot_create_package(end_user):
    hotel = HotelFactory()
    origin = City.objects.create(name="Buenos Aires")
    data = {
        "hotel": hotel.id,
        "origin": origin.id,
        "outbound_flight_id": 10,
        "outbound_flight_date": "2026-10-10T09:00:00Z",
        "return_flight_id": 11,
        "return_flight_date": "2026-10-17T18:00:00Z",
        "name": "No permitido",
        "description": "",
        "price": "100.00",
    }

    response = post(reverse("package-list"), data, user=end_user)

    assert response.status_code == HTTP_403_FORBIDDEN
