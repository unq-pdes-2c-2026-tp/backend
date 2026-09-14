import factory

from packages.models import Agency, Hotel, City


class AgencyFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")

    class Meta:
        model = Agency


class CityFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")

    class Meta:
        model = City


class HotelFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    city = factory.SubFactory(CityFactory)

    class Meta:
        model = Hotel
