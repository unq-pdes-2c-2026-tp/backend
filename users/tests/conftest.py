import pytest
from django.contrib.auth import get_user_model

from users.constants import UserType


User = get_user_model()


@pytest.fixture()
def admin_user():
    return User.objects.create_user(
        email="admin@mail.com",
        password="123",
        name="Pep",
        user_type=UserType.ADMIN,
    )


@pytest.fixture()
def end_user():
    return User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=UserType.END_USER.value,
    )


@pytest.fixture()
def agency_user():
    return User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=UserType.AGENCY.value,
    )
