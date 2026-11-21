from behave import given

from packages.tests.factories import AgencyFactory


@given("una agencia")
def agency(context):
    context.agency = AgencyFactory(name="viejo nombre")
