import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_200_OK,
)

from packages.models import Agency
from packages.tests.factories import AgencyFactory
from test_utils.views import post, get, patch, delete, put


@pytest.mark.django_db
def test_post_agency_creates_agency_when_user_is_admin(admin_user):
    response = post(reverse("agency-list"), {"name": "Nueva Agencia"}, user=admin_user)

    assert response.status_code == HTTP_201_CREATED

    qs = Agency.objects.filter(name="Nueva Agencia")
    assert qs.exists()


@pytest.mark.django_db
def test_post_agency_fails_when_name_already_exists(admin_user):
    AgencyFactory(name="Agencia Repetida")

    response = post(
        reverse("agency-list"), {"name": "Agencia Repetida"}, user=admin_user
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {"name": ["This field must be unique."]}


@pytest.mark.django_db
def test_post_agency_returns_unauthorized_when_user_is_end_user(end_user):
    response = post(reverse("agency-list"), {"name": "Nueva Agencia"}, user=end_user)

    assert response.status_code == HTTP_403_FORBIDDEN

    qs = Agency.objects.filter(name="Nueva Agencia")
    assert not qs.exists()


@pytest.mark.django_db
def test_post_agency_returns_unauthorized_when_user_is_agency(agency_user):
    response = post(reverse("agency-list"), {"name": "Nueva Agencia"}, user=agency_user)

    assert response.status_code == HTTP_403_FORBIDDEN

    qs = Agency.objects.filter(name="Nueva Agencia")
    assert not qs.exists()


@pytest.mark.django_db
def test_list_agencies_without_authentication():
    agency = AgencyFactory(name="Agencia")
    response = get(reverse("agency-list"))

    assert response.status_code == HTTP_200_OK

    assert response.json() == [{"id": agency.id, "name": "Agencia"}]


@pytest.mark.django_db
def test_patch_agency_returns_unauthorized_when_user_is_end_user(end_user):
    agency = AgencyFactory(name="Agencia")
    response = patch(
        reverse("agency-detail", kwargs={"pk": agency.id}),
        {"name": "Nueva Agencia"},
        user=end_user,
    )

    assert response.status_code == HTTP_403_FORBIDDEN

    qs = Agency.objects.filter(name="Nueva Agencia")
    assert not qs.exists()


@pytest.mark.django_db
def test_patch_agency_returns_unauthorized_when_user_is_agency(agency_user):
    agency = AgencyFactory(name="Agencia")
    response = patch(
        reverse("agency-detail", kwargs={"pk": agency.id}),
        {"name": "Nueva Agencia"},
        user=agency_user,
    )

    assert response.status_code == HTTP_403_FORBIDDEN

    qs = Agency.objects.filter(name="Nueva Agencia")
    assert not qs.exists()


@pytest.mark.django_db
def test_put_agency_returns_unauthorized_when_user_is_end_user(end_user):
    agency = AgencyFactory(name="Agencia")
    response = put(
        reverse("agency-detail", kwargs={"pk": agency.id}),
        {"name": "Nueva Agencia"},
        user=end_user,
    )

    assert response.status_code == HTTP_403_FORBIDDEN

    qs = Agency.objects.filter(name="Nueva Agencia")
    assert not qs.exists()


@pytest.mark.django_db
def test_put_agency_returns_unauthorized_when_user_is_agency(agency_user):
    agency = AgencyFactory(name="Agencia")
    response = put(
        reverse("agency-detail", kwargs={"pk": agency.id}),
        {"name": "Nueva Agencia"},
        user=agency_user,
    )

    assert response.status_code == HTTP_403_FORBIDDEN

    qs = Agency.objects.filter(name="Nueva Agencia")
    assert not qs.exists()


@pytest.mark.django_db
def test_delete_agency_returns_unauthorized_when_user_is_end_user(end_user):
    agency = AgencyFactory(name="Agencia")
    response = delete(reverse("agency-detail", kwargs={"pk": agency.id}), user=end_user)

    assert response.status_code == HTTP_403_FORBIDDEN

    qs = Agency.objects.filter(name="Agencia")
    assert qs.exists()


@pytest.mark.django_db
def test_delete_agency_returns_unauthorized_when_user_is_agency(agency_user):
    agency = AgencyFactory(name="Agencia")
    response = delete(
        reverse("agency-detail", kwargs={"pk": agency.id}), user=agency_user
    )

    assert response.status_code == HTTP_403_FORBIDDEN

    qs = Agency.objects.filter(name="Agencia")
    assert qs.exists()


@pytest.mark.django_db
def test_list_agencies_search_filters_by_name():
    agency1 = AgencyFactory(name="Agencia")
    agency2 = AgencyFactory(name="Lagencia")
    AgencyFactory(name="Carlitos travel")
    response = get(reverse("agency-list"), {"search": "agen"})

    assert response.status_code == HTTP_200_OK

    assert response.json() == [
        {"id": agency1.id, "name": "Agencia"},
        {"id": agency2.id, "name": "Lagencia"},
    ]
