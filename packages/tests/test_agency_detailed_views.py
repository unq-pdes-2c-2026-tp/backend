import pytest
from django.urls import reverse
from freezegun import freeze_time
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
)

from packages.tests.factories import (
    AgencyFactory,
    PackagePurchaseFactory,
    PackageReviewFactory,
)
from test_utils.views import get


@pytest.mark.django_db
def test_list_agencies_detailed_without_authentication():
    response = get(reverse("agency-list-detailed"))

    assert response.status_code == HTTP_401_UNAUTHORIZED


@freeze_time("2026-09-23")
@pytest.mark.django_db
def test_list_agencies_detailed_returns_total_revenue_for_this_month(
    end_user, admin_user
):
    agency = AgencyFactory(name="Agencia")
    PackagePurchaseFactory(package__agency=agency, price=2000, user=end_user)

    with freeze_time("2026-08-23"):
        PackagePurchaseFactory(package__agency=agency, price=1000, user=end_user)

    response = get(reverse("agency-list-detailed"), user=admin_user)

    assert response.status_code == HTTP_200_OK

    assert response.json()[0]["total_revenue"] == "2000.00"


@freeze_time("2026-09-23")
@pytest.mark.django_db
def test_list_agencies_detailed_returns_agencies_without_purchases(
    end_user, admin_user
):
    AgencyFactory(name="Agencia")

    response = get(reverse("agency-list-detailed"), user=admin_user)

    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["total_revenue"] == "0.00"


@freeze_time("2026-09-23")
@pytest.mark.django_db
def test_list_agencies_detailed_returns_avg_score(end_user, admin_user):
    agency = AgencyFactory(name="Agencia")
    purchase1 = PackagePurchaseFactory(
        package__agency=agency, price=2000, user=end_user
    )
    PackageReviewFactory(package_purchase=purchase1, score=10)

    with freeze_time("2026-08-23"):
        purchase2 = PackagePurchaseFactory(
            package__agency=agency, price=1000, user=end_user
        )
        PackageReviewFactory(package_purchase=purchase2, score=8)
    response = get(reverse("agency-list-detailed"), user=admin_user)

    assert response.status_code == HTTP_200_OK

    assert response.json()[0]["avg_score"] == "9.0"


@freeze_time("2026-09-23")
@pytest.mark.django_db
def test_list_agencies_detailed_returns_none_when_agency_has_no_purchases(
    end_user, admin_user
):
    AgencyFactory(name="Agencia")

    response = get(reverse("agency-list-detailed"), user=admin_user)

    assert response.status_code == HTTP_200_OK

    assert response.json()[0]["avg_score"] is None
