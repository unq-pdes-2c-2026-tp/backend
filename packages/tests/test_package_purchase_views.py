from decimal import Decimal
from unittest.mock import Mock, patch
import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)

from packages.models import PackagePurchase
from packages.tests.factories import PackageFactory, PackagePurchaseFactory
from test_utils.views import get, post


@pytest.mark.django_db
@patch("packages.serializers.FlightAPIClient.buy_flight")
def test_end_user_can_purchase_package_when_flights_are_available(mock_post, end_user):
    mock_post.return_value = Mock(status_code=201)
    package = PackageFactory()

    response = post(
        reverse("packagepurchase-list"),
        {"package": package.id},
        user=end_user,
    )

    assert response.status_code == HTTP_201_CREATED
    assert PackagePurchase.objects.count() == 1

    purchase = PackagePurchase.objects.first()
    assert purchase.package == package
    assert purchase.user == end_user
    assert purchase.price == Decimal("150000.00")

    # Llamados a la API de vuelos para la ida y la vuelta
    assert mock_post.call_count == 2

    first_call_args = mock_post.call_args_list[0].args
    assert first_call_args == (
        package.outbound_flight_id,
        end_user.name,
        end_user.email,
    )

    second_call_args = mock_post.call_args_list[1].args
    assert second_call_args == (package.return_flight_id, end_user.name, end_user.email)


@pytest.mark.django_db
@patch("packages.serializers.FlightAPIClient.buy_flight")
def test_purchase_fails_when_flights_api_is_unreachable(mock_post, end_user):
    import requests

    mock_post.side_effect = requests.RequestException("Error de conexion")
    package = PackageFactory()

    response = post(
        reverse("packagepurchase-list"),
        {"package": package.id},
        user=end_user,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert PackagePurchase.objects.count() == 0


@pytest.mark.django_db
def test_non_end_user_cannot_purchase_package(agency_user):
    package = PackageFactory()

    response = post(
        reverse("packagepurchase-list"),
        {"package": package.id},
        user=agency_user,
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert PackagePurchase.objects.count() == 0


@pytest.mark.django_db
def test_list_purchases_returns_user_purchases(end_user):
    purchase = PackagePurchaseFactory(user=end_user)

    response = get(reverse("packagepurchase-list"), user=end_user)

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == purchase.id
    assert data[0]["package"] == purchase.package.id
