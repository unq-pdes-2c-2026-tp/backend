import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
)

from packages.tests.factories import HotelFactory, CityFactory
from test_utils.views import get


@pytest.mark.django_db
def test_list_hotels_without_authentication():
    hotel = HotelFactory(name="howard johnson")
    response = get(reverse("hotel-list"))

    assert response.status_code == HTTP_200_OK

    assert response.json() == [
        {
            "id": hotel.id,
            "name": "howard johnson",
            "description": "",
            "photo": None,
            "city": hotel.city.id,
        }
    ]


@pytest.mark.django_db
def test_list_hotels_search_filters_by_name():
    hotel = HotelFactory(name="hotel")
    motel = HotelFactory(name="motel")
    HotelFactory(name="Stanley")
    response = get(reverse("hotel-list"), {"search": "otel"})

    assert response.status_code == HTTP_200_OK

    data = response.json()
    assert len(data) == 2
    assert any(item["id"] == hotel.id for item in data)
    assert any(item["id"] == motel.id for item in data)


@pytest.mark.django_db
def test_list_hotels_search_filters_by_description():
    hotel = HotelFactory(description="lindo lugar")
    motel = HotelFactory(description="re LINDO")
    HotelFactory(description="medio feo")
    response = get(reverse("hotel-list"), {"search": "lindo"})

    assert response.status_code == HTTP_200_OK

    data = response.json()
    assert len(data) == 2
    assert any(item["id"] == hotel.id for item in data)
    assert any(item["id"] == motel.id for item in data)


@pytest.mark.django_db
def test_list_hotels_search_filters_by_city_name():
    hotel = HotelFactory(city=CityFactory(name="buenos aires"))
    motel = HotelFactory(city=CityFactory(name="BUEN ayre"))
    HotelFactory(city=CityFactory(name="catamarca"))
    response = get(reverse("hotel-list"), {"search": "buen"})

    assert response.status_code == HTTP_200_OK

    data = response.json()
    assert len(data) == 2
    assert any(item["id"] == hotel.id for item in data)
    assert any(item["id"] == motel.id for item in data)
