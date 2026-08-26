import factory

from packages.models import Agency


class AgencyFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")

    class Meta:
        model = Agency
