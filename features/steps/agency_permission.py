from behave import given, when, then
from django.urls import reverse
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_201_CREATED

from packages.models import Agency
from test_utils.views import post
from users.constants import UserType
from users.tests.factories import UserFactory


@given("un usuario final")
def end_user(context):
    context.user = UserFactory(user_type=UserType.END_USER)


@given("un usuario agencia")
def agency_user(context):
    context.user = UserFactory(user_type=UserType.AGENCY)


@given("un usuario administrador")
def admin_user(context):
    context.user = UserFactory(user_type=UserType.ADMIN)


@when("intenta crear una agencia")
def create_agency(context):
    response = post(
        reverse("agency-list"), {"name": "Nueva Agencia"}, user=context.user
    )

    context.response = response


@then("un error de permisos insuficientes es devuelto.")
def assert_403(context):
    assert context.response.status_code == HTTP_403_FORBIDDEN


@then("la agencia es creada correctamente")
def assert_agency_created(context):
    assert context.response.status_code == HTTP_201_CREATED
    assert Agency.objects.filter(name="Nueva Agencia").exists()
