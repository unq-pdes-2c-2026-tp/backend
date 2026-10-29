from unittest.mock import patch, MagicMock

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
    instance = get_flights_api_client()
    with patch(
        "packages.management.commands.init_defaults.FlightAPIClient",
        return_value=instance,
    ):
        call_command("init_defaults")
    user = User.objects.get(email=created_user_data["email"])
    assert user.user_type == created_user_data["user_type"]
    assert user.check_password(created_user_data["password"])
    assert (
        user.agency is None
        if created_user_data["agency_is_null"]
        else user.agency is not None
    )


def get_flights_api_client() -> MagicMock:
    instance = MagicMock()
    instance.get_flights.return_value = {
        "results": [
            {
                "id": 3,
                "fecha": "2026-03-03",
                "hora": "12:30:00",
                "origen": "san carlos de bariloche",
                "destino": "Buenos Aires",
            },
            {
                "id": 5,
                "fecha": "2026-04-03",
                "hora": "12:30:00",
                "origen": "Mendoza",
                "destino": "Buenos Aires",
            },
            {
                "id": 6,
                "fecha": "2026-04-13",
                "hora": "12:30:00",
                "origen": "Buenos Aires",
                "destino": "Mendoza",
            },
            {
                "id": 7,
                "fecha": "2026-04-03",
                "hora": "12:30:00",
                "origen": "Puerto Iguazú",
                "destino": "Buenos Aires",
            },
            {
                "id": 8,
                "fecha": "2026-04-13",
                "hora": "12:30:00",
                "origen": "Buenos Aires",
                "destino": "Puerto Iguazú",
            },
            {
                "id": 4,
                "fecha": "2026-03-10",
                "hora": "12:30:00",
                "origen": "buenos aires",
                "destino": "san carlos de bariloche",
            },
        ]
    }
    return instance


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
    instance = get_flights_api_client()
    with patch(
        "packages.management.commands.init_defaults.FlightAPIClient",
        return_value=instance,
    ):
        call_command("init_defaults")
    assert Agency.objects.filter(**agencies_data).exists()
