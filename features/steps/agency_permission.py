from behave import given, when, then
from django.urls import reverse
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_201_CREATED, HTTP_200_OK

from packages.models import Agency
from packages.tests.factories import AgencyFactory
from test_utils.views import post, patch
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


@given("una agencia")
def agency(context):
    context.agency = AgencyFactory(name="viejo nombre")


@when("intenta crear una agencia")
def create_agency(context):
    response = post(
        reverse("agency-list"), {"name": "Nueva Agencia"}, user=context.user
    )

    context.response = response


@when("intenta modificar una agencia")
def update_agency(context):
    response = patch(
        reverse("agency-detail", kwargs={"pk": context.agency.id}),
        {"name": "Nuevo nombre"},
        user=context.user,
    )

    context.response = response


@then("un error de permisos insuficientes es devuelto")
def assert_403(context):
    print(context.response.status_code)
    assert context.response.status_code == HTTP_403_FORBIDDEN


@then("la agencia es creada correctamente")
def assert_agency_created(context):
    assert context.response.status_code == HTTP_201_CREATED
    assert Agency.objects.filter(name="Nueva Agencia").exists()


@then("la agencia es modificada correctamente")
def assert_agency_updated(context):
    assert context.response.status_code == HTTP_200_OK
    assert Agency.objects.filter(name="Nuevo nombre").exists()
