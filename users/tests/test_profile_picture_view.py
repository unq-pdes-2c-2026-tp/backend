import pytest
from django.contrib.auth import get_user_model
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from test_utils.views import post, delete
from users.constants import UserType
from users.tests.utils import make_image


User = get_user_model()


@pytest.mark.django_db
def test_post_profile_picture():
    user = User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=UserType.END_USER.value,
    )
    response = post(
        "/api/users/profile-picture/",
        {"profile_picture": make_image()},
        fmt="multipart",
        user=user,
    )
    assert response.status_code == HTTP_200_OK

    user.refresh_from_db()
    assert user.profile_picture
    user.profile_picture.delete()


@pytest.mark.django_db
def test_delete_profile_picture():
    user = User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=UserType.END_USER.value,
        profile_picture=make_image(),
    )
    response = delete("/api/users/profile-picture/", user=user)
    assert response.status_code == HTTP_204_NO_CONTENT

    user.refresh_from_db()
    assert not user.profile_picture


@pytest.mark.django_db
def test_delete_profile_picture_when_user_has_no_profile_picture():
    user = User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=UserType.END_USER.value,
    )
    response = delete("/api/users/profile-picture/", user=user)
    assert response.status_code == HTTP_404_NOT_FOUND
