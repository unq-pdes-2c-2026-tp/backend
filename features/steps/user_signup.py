from behave import given, when, then
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from packages.tests.factories import AgencyFactory
from test_utils.views import post


User = get_user_model()


@given("un usuario final")
def end_user(context):
    context.user_payload = {
        "email": "mail@mail.com",
        "user_type": 1,
        "name": "usuario",
        "password": settings.TESTING_PASSWORD,
    }


@given("un usuario agencia")
def agency_user(context):
    context.user_payload = {
        "email": "mail@mail.com",
        "user_type": 2,
        "name": "usuario",
        "password": settings.TESTING_PASSWORD,
    }


@given("un usuario administrador")
def admin_user(context):
    context.user_payload = {
        "email": "mail@mail.com",
        "user_type": 3,
        "name": "usuario",
        "password": settings.TESTING_PASSWORD,
    }


@given("una agencia")
def agency(context):
    context.agency = AgencyFactory(name="viejo nombre")


@when("intenta crear una cuenta sin agencia")
def create_user_without_agency(context):
    response = post(reverse("user-list"), context.user_payload)

    context.response = response


@when("intenta crear una cuenta con agencia")
def create_user_with_agency(context):
    paylaod = context.user_payload
    paylaod["agency"] = context.agency.id
    response = post(reverse("user-list"), context.user_payload)

    context.response = response


@then("un error de validacion es devuelto")
def assert_400(context):
    assert context.response.status_code == HTTP_400_BAD_REQUEST
    assert context.response.errors == 3


@then("el usuario es creado y la agencia es nula")
def assert_user_created_with_agency_none(context):
    assert context.response.status_code == HTTP_201_CREATED
    assert User.objects.filter(name="usuario").exists()
    assert User.objects.filter(name="usuario").count() == 1
    assert User.objects.get(name="usuario").agency is None


@then("el usuario es creado y la agencia esta asociada")
def assert_user_created_with_agency(context):
    assert context.response.status_code == HTTP_201_CREATED
    assert User.objects.filter(name="usuario").exists()
    assert User.objects.filter(name="usuario").count() == 1
    assert User.objects.get(name="usuario").agency == context.agency
