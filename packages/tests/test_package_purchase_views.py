from decimal import Decimal
from unittest.mock import Mock, patch
import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
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


@pytest.mark.django_db
def test_list_purchases_returns_only_own_purchases_for_end_user(end_user, agency_user):
    user_purchase = PackagePurchaseFactory(user=end_user)
    PackagePurchaseFactory(user=agency_user)  # Compra asociada a otro usuario

    response = get(reverse("packagepurchase-list"), user=end_user)

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == user_purchase.id
    assert data[0]["package"] == user_purchase.package.id


@pytest.mark.django_db
def test_list_purchases_returns_only_agency_sales_for_agency_user(
    agency_user, end_user
):
    agency_package = PackageFactory(agency=agency_user.agency)
    agency_sale = PackagePurchaseFactory(package=agency_package, user=end_user)
    PackagePurchaseFactory(user=end_user)  # Venta de otra agencia

    response = get(reverse("packagepurchase-list"), user=agency_user)

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == agency_sale.id
    assert data[0]["package"] == agency_package.id


@pytest.mark.django_db
def test_list_purchases_returns_all_purchases_for_admin(admin_user, end_user):
    purchase_1 = PackagePurchaseFactory(user=end_user)
    purchase_2 = PackagePurchaseFactory(user=end_user)

    response = get(reverse("packagepurchase-list"), user=admin_user)

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert {item["id"] for item in data} == {purchase_1.id, purchase_2.id}


@pytest.mark.django_db
def test_unauthenticated_user_cannot_list_purchases(end_user):
    PackagePurchaseFactory(user=end_user)

    response = get(reverse("packagepurchase-list"))

    assert response.status_code in (HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_end_user_cannot_retrieve_other_user_purchase(end_user, agency_user):
    other_purchase = PackagePurchaseFactory(user=agency_user)

    response = get(
        reverse("packagepurchase-detail", args=[other_purchase.id]),
        user=end_user,
    )

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_agency_user_cannot_retrieve_other_agency_sale(agency_user, end_user):
    other_sale = PackagePurchaseFactory(user=end_user)

    response = get(
        reverse("packagepurchase-detail", args=[other_sale.id]),
        user=agency_user,
    )

    assert response.status_code == HTTP_404_NOT_FOUND
