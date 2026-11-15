import pytest
from django.contrib.auth import get_user_model

from packages.tests.factories import AgencyFactory
from users.constants import UserType


User = get_user_model()


@pytest.fixture()
def admin_user():
    return User.objects.create_user(
        email="admin@mail.com",
        password="123",
        name="Admin",
        user_type=UserType.ADMIN.value,
    )


@pytest.fixture()
def end_user():
    return User.objects.create_user(
        email="enduser@mail.com",
        password="123",
        name="End User",
        user_type=UserType.END_USER.value,
    )


@pytest.fixture()
def agency_user():
    return User.objects.create_user(
        email="agency@mail.com",
        password="123",
        name="Agency User",
        user_type=UserType.AGENCY.value,
        agency=AgencyFactory(),
    )
