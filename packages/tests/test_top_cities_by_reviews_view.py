import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
)

from packages.tests.factories import (
    PackagePurchaseFactory,
    CityFactory,
    PackageReviewFactory,
)
from test_utils.views import get
from users.constants import UserType
from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_top_cities_by_reviews_limits_to_five_cities(admin_user, end_user):
    first_city_id = None
    for n in range(6):
        city = CityFactory()
        first_city_id = first_city_id or city.id
        for i in range(2):
            purchase = PackagePurchaseFactory(
                package__hotel__city=city, user=end_user, price=1000
            )
            PackageReviewFactory(package_purchase=purchase, score=i + 1 + n)
    response = get(reverse("packagepurchase-top-cities-by-reviews"), user=admin_user)

    assert response.status_code == HTTP_200_OK
    results = response.json()
    assert len(results) == 5
    assert first_city_id not in [result["city"]["id"] for result in results]
    assert {"2.50", "3.50", "4.50", "5.50", "6.50"} == {
        result["avg_reviews"] for result in results
    }


@pytest.mark.parametrize("user_type", (UserType.AGENCY, UserType.END_USER))
@pytest.mark.django_db
def test_top_cities_by_reviews_is_restricted_to_admins(user_type):
    user = UserFactory(user_type=user_type)
    response = get(reverse("packagepurchase-top-cities-by-reviews"), user=user)

    assert response.status_code == HTTP_403_FORBIDDEN
