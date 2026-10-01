import pytest
from django.contrib.auth import get_user_model
from rest_framework.status import HTTP_200_OK

from test_utils.views import post
from users.constants import UserType
from users.tests.utils import make_image

User = get_user_model()


@pytest.mark.django_db
def test_login_with_valid_credentials_response():
    user = User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=UserType.END_USER.value,
    )
    response = post("/api/login/", {"email": "test@mail.com", "password": "123"})

    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "agency": None,
        "email": "test@mail.com",
        "id": user.id,
        "name": "Pep",
        "user_type": user.user_type,
        "profile_picture": None,
    }


@pytest.mark.django_db
def test_login_with_valid_credentials_response_headers():
    User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=UserType.END_USER.value,
    )
    response = post("/api/login/", {"email": "test@mail.com", "password": "123"})

    assert response.status_code == HTTP_200_OK
    assert "authorization" in response.headers


@pytest.mark.django_db
def test_login_includes_profile_picture_url():
    user = User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=UserType.END_USER.value,
        profile_picture=make_image(),
    )
    response = post("/api/login/", {"email": "test@mail.com", "password": "123"})

    assert response.status_code == HTTP_200_OK
    assert response.json()["profile_picture"] == (
        f"http://testserver{user.profile_picture.url}"
    )
    user.profile_picture.delete()
