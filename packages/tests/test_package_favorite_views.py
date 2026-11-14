import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from packages.models import PackageFavorite
from packages.tests.factories import PackageFactory, PackageFavoriteFactory
from test_utils.views import delete, get, post
from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_end_user_can_add_package_to_favorites(end_user):
    package = PackageFactory()

    response = post(
        reverse("packagefavorite-list"),
        {"package": package.id},
        user=end_user,
    )

    assert response.status_code == HTTP_201_CREATED
    assert PackageFavorite.objects.count() == 1

    favorite = PackageFavorite.objects.first()
    assert favorite.package == package
    assert favorite.user == end_user


@pytest.mark.django_db
def test_end_user_cannot_favorite_same_package_twice(end_user):
    favorite = PackageFavoriteFactory(user=end_user)

    response = post(
        reverse("packagefavorite-list"),
        {"package": favorite.package.id},
        user=end_user,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert PackageFavorite.objects.count() == 1


@pytest.mark.django_db
def test_non_end_user_cannot_add_package_to_favorites(agency_user):
    package = PackageFactory()

    response = post(
        reverse("packagefavorite-list"),
        {"package": package.id},
        user=agency_user,
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert PackageFavorite.objects.count() == 0


@pytest.mark.django_db
def test_list_favorites_returns_only_user_favorites(end_user):
    other_user = UserFactory()
    user_favorite = PackageFavoriteFactory(user=end_user)
    PackageFavoriteFactory(user=other_user)

    response = get(reverse("packagefavorite-list"), user=end_user)

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == user_favorite.id
    assert data[0]["package"] == user_favorite.package.id


@pytest.mark.django_db
def test_end_user_can_delete_own_favorite(end_user):
    favorite = PackageFavoriteFactory(user=end_user)

    response = delete(
        reverse("packagefavorite-detail", kwargs={"pk": favorite.id}),
        user=end_user,
    )

    assert response.status_code == HTTP_204_NO_CONTENT
    assert PackageFavorite.objects.count() == 0


@pytest.mark.django_db
def test_end_user_cannot_delete_other_user_favorite(end_user):
    other_user = UserFactory()
    other_favorite = PackageFavoriteFactory(user=other_user)

    response = delete(
        reverse("packagefavorite-detail", kwargs={"pk": other_favorite.id}),
        user=end_user,
    )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert PackageFavorite.objects.count() == 1
