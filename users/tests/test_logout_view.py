import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_200_OK

from test_utils.views import post
from users.constants import UserType

User = get_user_model()


@pytest.mark.django_db
def test_logout_view():
    user = User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=UserType.END_USER.value,
    )
    token = Token(user=user)
    token.save()

    response = post("/api/logout/", {}, user=user, token=token)

    assert response.status_code == HTTP_200_OK
    assert not Token.objects.exists()
