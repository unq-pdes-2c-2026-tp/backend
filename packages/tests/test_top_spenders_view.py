import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
)

from packages.tests.factories import PackagePurchaseFactory
from test_utils.views import get
from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_top_spenders_limits_to_five_users(admin_user):
    first_user_id = None
    for n in range(6):
        user = UserFactory()
        first_user_id = first_user_id or user.id
        PackagePurchaseFactory(user=user, price=(n + 1) * 1000)

    response = get(reverse("packagepurchase-top-spenders"), user=admin_user)

    assert response.status_code == HTTP_200_OK
    results = response.json()
    assert len(results) == 5
    assert first_user_id not in [result["user"]["id"] for result in results]
