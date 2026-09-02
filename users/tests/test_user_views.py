import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.test import APIClient

from packages.tests.factories import AgencyFactory
from test_utils.views import post, get
from users.constants import UserType
from users.tests.utils import make_image

User = get_user_model()


@pytest.mark.django_db
def test_post_user_allows_frontend_origin():
    client = APIClient()
    response = client.post(
        reverse("user-list"),
        {
            "email": "test@mail.com",
            "user_type": UserType.END_USER.value,
            "name": "pepe",
            "password": "contra-seña",
        },
        HTTP_ORIGIN="http://localhost:5173",
        format="json",
    )

    assert response.status_code == HTTP_201_CREATED
    assert response["Access-Control-Allow-Origin"] == "http://localhost:5173"


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
def test_post_user_fails_when_user_with_the_same_mail_exists(end_user):
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


@pytest.mark.django_db
def test_get_user(end_user):
    response = get(
        reverse("user-detail", kwargs={"pk": end_user.id}),
    )

    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "id": end_user.pk,
        "name": "Pep",
        "email": "test@mail.com",
        "user_type": end_user.user_type,
        "agency": None,
        "profile_picture": None,
    }


@pytest.mark.django_db
def test_get_user_with_profile_picture():
    user = User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=UserType.END_USER.value,
        profile_picture=make_image(),
    )
    response = get(
        reverse("user-detail", kwargs={"pk": user.id}),
    )
    user.profile_picture.delete()
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "id": user.pk,
        "name": "Pep",
        "email": "test@mail.com",
        "user_type": user.user_type,
        "agency": None,
        "profile_picture": "http://testserver/test_image.jpg",
    }
