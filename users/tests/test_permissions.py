from unittest.mock import MagicMock

import pytest
from django.contrib.auth import get_user_model

from users.constants import UserType
from users.permissions import EndUserPermission, AgencyPermission, AdminPermission

User = get_user_model()


@pytest.mark.parametrize(
    ("user_type", "permission_class"),
    (
        (UserType.END_USER, EndUserPermission),
        (UserType.AGENCY, AgencyPermission),
        (UserType.ADMIN, AdminPermission),
    ),
)
@pytest.mark.django_db
def test_user_type_permissions(user_type, permission_class):
    user = User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=user_type,
    )
    request = MagicMock()
    request.user = user
    assert permission_class().has_permission(request, None)
    assert permission_class().has_object_permission(request, None, None)


@pytest.mark.parametrize(
    ("user_type", "permission_classes"),
    (
        (UserType.END_USER, (AgencyPermission, AdminPermission)),
        (UserType.AGENCY, (EndUserPermission, AdminPermission)),
        (UserType.ADMIN, (EndUserPermission, AgencyPermission)),
    ),
)
@pytest.mark.django_db
def test_user_type_permissions_denial(user_type, permission_classes):
    user = User.objects.create_user(
        email="test@mail.com",
        password="123",
        name="Pep",
        user_type=user_type,
    )
    request = MagicMock()
    request.user = user
    for permission_class in permission_classes:
        assert not permission_class().has_permission(request, None)
        assert not permission_class().has_object_permission(request, None, None)
