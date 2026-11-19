import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from packages.models import PackageReview
from packages.tests.factories import (
    PackageFactory,
    PackagePurchaseFactory,
    PackageReviewFactory,
)
from test_utils.views import get, patch, post, put


@pytest.mark.django_db
def test_end_user_can_create_review_for_own_purchase(end_user):
    purchase = PackagePurchaseFactory(user=end_user)

    response = post(
        reverse("packagereview-list"),
        {
            "package_purchase": purchase.id,
            "score": 9,
            "review": "Excelente paquete y atención",
        },
        user=end_user,
    )

    assert response.status_code == HTTP_201_CREATED
    assert PackageReview.objects.count() == 1

    review = PackageReview.objects.first()
    assert review.package_purchase == purchase
    assert review.score == 9
    assert review.review == "Excelente paquete y atención"


@pytest.mark.django_db
def test_end_user_cannot_create_review_for_other_user_purchase(end_user, agency_user):
    other_purchase = PackagePurchaseFactory(user=agency_user)

    response = post(
        reverse("packagereview-list"),
        {
            "package_purchase": other_purchase.id,
            "score": 5,
            "review": "No es mi compra",
        },
        user=end_user,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert PackageReview.objects.count() == 0


@pytest.mark.django_db
def test_end_user_cannot_create_duplicate_review_for_same_purchase(end_user):
    purchase = PackagePurchaseFactory(user=end_user)
    PackageReviewFactory(package_purchase=purchase)

    response = post(
        reverse("packagereview-list"),
        {
            "package_purchase": purchase.id,
            "score": 10,
            "review": "Segunda reseña",
        },
        user=end_user,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert PackageReview.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("invalid_score", [-1, 11])
def test_create_review_fails_with_out_of_range_score(end_user, invalid_score):
    purchase = PackagePurchaseFactory(user=end_user)

    response = post(
        reverse("packagereview-list"),
        {
            "package_purchase": purchase.id,
            "score": invalid_score,
            "review": "Puntaje inválido",
        },
        user=end_user,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert PackageReview.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("user_fixture", ["agency_user", "admin_user"])
def test_non_end_user_cannot_create_review(request, end_user, user_fixture):
    user = request.getfixturevalue(user_fixture)
    purchase = PackagePurchaseFactory(user=end_user)

    response = post(
        reverse("packagereview-list"),
        {
            "package_purchase": purchase.id,
            "score": 8,
            "review": "Reseña no permitida",
        },
        user=user,
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert PackageReview.objects.count() == 0


@pytest.mark.django_db
def test_end_user_can_partial_update_own_review(end_user):
    purchase = PackagePurchaseFactory(user=end_user)
    review = PackageReviewFactory(
        package_purchase=purchase, score=6, review="Estuvo bien"
    )

    response = patch(
        reverse("packagereview-detail", args=[review.id]),
        {"score": 10, "review": "Mejoró mucho al final"},
        user=end_user,
    )

    assert response.status_code == HTTP_200_OK
    review.refresh_from_db()
    assert review.score == 10
    assert review.review == "Mejoró mucho al final"


@pytest.mark.django_db
def test_end_user_can_full_update_own_review_without_changing_purchase(end_user):
    purchase_1 = PackagePurchaseFactory(user=end_user)
    purchase_2 = PackagePurchaseFactory(user=end_user)
    review = PackageReviewFactory(
        package_purchase=purchase_1, score=7, review="Original"
    )

    response = put(
        reverse("packagereview-detail", args=[review.id]),
        {
            "package_purchase": purchase_2.id,
            "score": 9,
            "review": "Actualizado",
        },
        user=end_user,
    )

    assert response.status_code == HTTP_200_OK
    review.refresh_from_db()
    assert review.package_purchase == purchase_1
    assert review.score == 9
    assert review.review == "Actualizado"


@pytest.mark.django_db
def test_end_user_cannot_update_other_user_review(end_user, agency_user):
    other_purchase = PackagePurchaseFactory(user=agency_user)
    other_review = PackageReviewFactory(package_purchase=other_purchase, score=5)

    response = patch(
        reverse("packagereview-detail", args=[other_review.id]),
        {"score": 1},
        user=end_user,
    )

    assert response.status_code == HTTP_404_NOT_FOUND
    other_review.refresh_from_db()
    assert other_review.score == 5


@pytest.mark.django_db
def test_list_reviews_returns_only_own_reviews_for_end_user(end_user, agency_user):
    own_purchase = PackagePurchaseFactory(user=end_user)
    own_review = PackageReviewFactory(package_purchase=own_purchase)

    other_purchase = PackagePurchaseFactory(user=agency_user)
    PackageReviewFactory(package_purchase=other_purchase)

    response = get(reverse("packagereview-list"), user=end_user)

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == own_review.id
    assert data[0]["package_purchase"] == own_purchase.id


@pytest.mark.django_db
def test_list_reviews_returns_only_agency_package_reviews_for_agency_user(
    agency_user, end_user
):
    agency_package = PackageFactory(agency=agency_user.agency)
    agency_purchase = PackagePurchaseFactory(package=agency_package, user=end_user)
    agency_review = PackageReviewFactory(package_purchase=agency_purchase)

    other_purchase = PackagePurchaseFactory(user=end_user)
    PackageReviewFactory(package_purchase=other_purchase)

    response = get(reverse("packagereview-list"), user=agency_user)

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == agency_review.id
    assert data[0]["package_id"] == agency_package.id


@pytest.mark.django_db
def test_list_reviews_returns_all_reviews_for_admin(admin_user, end_user):
    review_1 = PackageReviewFactory(
        package_purchase=PackagePurchaseFactory(user=end_user)
    )
    review_2 = PackageReviewFactory(
        package_purchase=PackagePurchaseFactory(user=end_user)
    )

    response = get(reverse("packagereview-list"), user=admin_user)

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert {item["id"] for item in data} == {review_1.id, review_2.id}


@pytest.mark.django_db
def test_list_reviews_can_filter_by_package_query_param(admin_user, end_user):
    package_1 = PackageFactory()
    package_2 = PackageFactory()

    review_1 = PackageReviewFactory(
        package_purchase=PackagePurchaseFactory(package=package_1, user=end_user)
    )
    PackageReviewFactory(
        package_purchase=PackagePurchaseFactory(package=package_2, user=end_user)
    )

    response = get(
        f"{reverse('packagereview-list')}?package={package_1.id}",
        user=admin_user,
    )

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == review_1.id


@pytest.mark.django_db
def test_unauthenticated_user_cannot_list_reviews(end_user):
    PackageReviewFactory(package_purchase=PackagePurchaseFactory(user=end_user))

    response = get(reverse("packagereview-list"))

    assert response.status_code in (HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN)
