import pytest
from django.urls import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from packages.models import Agency
from packages.tests.factories import AgencyFactory
from test_utils.views import post


@pytest.mark.django_db
def test_post_agency_creates_agency():
    response = post(reverse("agency-list"), {"name": "Nueva Agencia"})

    assert response.status_code == HTTP_201_CREATED

    qs = Agency.objects.filter(name="Nueva Agencia")
    assert qs.exists()


@pytest.mark.django_db
def test_post_agency_fails_when_name_already_exists():
    AgencyFactory(name="Agencia Repetida")

    response = post(reverse("agency-list"), {"name": "Agencia Repetida"})

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {"name": ["This field must be unique."]}
