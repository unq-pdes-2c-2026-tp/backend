import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from packages.models import Agency
from users.constants import UserType


User = get_user_model()


@pytest.mark.parametrize(
    "created_user_data",
    [
        {
            "email": "admin@gmail.com",
            "user_type": UserType.ADMIN,
            "password": "admin",
            "agency_is_null": True,
        },
        {
            "email": "user@gmail.com",
            "user_type": UserType.END_USER,
            "password": "user",
            "agency_is_null": True,
        },
        {
            "email": "agency@gmail.com",
            "user_type": UserType.AGENCY,
            "password": "agency",
            "agency_is_null": False,
        },
    ],
)
@pytest.mark.django_db
def test_init_defaults_create_one_user_of_each_type(created_user_data):
    call_command("init_defaults")
    user = User.objects.get(email=created_user_data["email"])
    assert user.user_type == created_user_data["user_type"]
    assert user.check_password(created_user_data["password"])
    assert (
        user.agency is None
        if created_user_data["agency_is_null"]
        else user.agency is not None
    )


@pytest.mark.parametrize(
    "agencies_data",
    [
        {"name": "Despegar"},
        {"name": "Turismo City"},
        {"name": "Juliá Tours"},
        {"name": "Costa Azul Viajes"},
        {"name": "Argentinian Explorer"},
        {"name": "Tangol"},
        {"name": "Biblos Travel"},
        {"name": "Eves"},
        {"name": "Pezzati Viajes"},
        {"name": "ANDA Travel"},
    ],
)
@pytest.mark.django_db
def test_init_defaults_creates_agencies(agencies_data):
    call_command("init_defaults")
    assert Agency.objects.filter(**agencies_data).exists()
