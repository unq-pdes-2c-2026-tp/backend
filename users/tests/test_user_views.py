import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from packages.tests.factories import AgencyFactory
from test_utils.views import post
from users.constants import UserType

User = get_user_model()


@pytest.mark.django_db
def test_post_user_creates_user():
    response = post(
        reverse("user-list"),
        {
            "email": "test@mail.com",
            "user_type": UserType.END_USER.value,
            "name": "pepe",
            "password": "contra-seña",
        },
    )
    assert response.status_code == HTTP_201_CREATED

    qs = User.objects.filter(
        email="test@mail.com", user_type=UserType.END_USER.value, name="pepe"
    )
    assert qs.exists()
    assert qs.first().check_password("contra-seña")


@pytest.mark.django_db
def test_post_user_fails_when_user_with_the_same_mail_exists():
    User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=UserType.END_USER.value,
    )
    response = post(
        reverse("user-list"),
        {
            "email": "test@mail.com",
            "user_type": UserType.END_USER.value,
            "name": "pepe",
            "password": "contra-seña",
        },
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {"email": ["This field must be unique."]}


@pytest.mark.django_db
def test_post_user_fails_when_user_type_is_agency_and_agency_is_missing():
    response = post(
        reverse("user-list"),
        {
            "email": "test@mail.com",
            "user_type": UserType.AGENCY.value,
            "name": "pepe",
            "password": "contra-seña",
        },
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {
        "agency": ["This field is required for user type agency."]
    }


@pytest.mark.django_db
def test_post_user_is_created_with_agency_related():
    agency = AgencyFactory()
    response = post(
        reverse("user-list"),
        {
            "email": "test@mail.com",
            "user_type": UserType.AGENCY.value,
            "name": "pepe",
            "password": "contra-seña",
            "agency": agency.pk,
        },
    )
    assert response.status_code == HTTP_201_CREATED
    qs = User.objects.filter(
        email="test@mail.com",
        user_type=UserType.AGENCY.value,
        name="pepe",
        agency=agency,
    )
    assert qs.exists()
