from behave import given, when, then
from django.urls import reverse
from rest_framework.status import HTTP_403_FORBIDDEN

from test_utils.views import post
from users.constants import UserType
from users.tests.factories import UserFactory


@given("un usuario final")
def end_user(context):
    context.test.user = UserFactory(user_type=UserType.END_USER)


@when("intenta crear una agencia")
def create_agency(context):
    response = post(
        reverse("agency-list"), {"name": "Nueva Agencia"}, user=context.test.user
    )

    context.test.response = response


@then("un error de permisos insuficientes es devuelto.")
def assert_403(context):
    assert context.test.response.status_code == HTTP_403_FORBIDDEN
