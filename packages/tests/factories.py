import factory
from decimal import Decimal
from django.utils import timezone
from packages.models import Agency, Hotel, City, Package, PackagePurchase


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


class PackageFactory(factory.django.DjangoModelFactory):
    agency = factory.SubFactory(AgencyFactory)
    hotel = factory.SubFactory(HotelFactory)
    origin = factory.SubFactory(CityFactory)
    outbound_flight_id = 10
    outbound_flight_date = factory.LazyFunction(timezone.now)
    return_flight_id = 20
    return_flight_date = factory.LazyFunction(timezone.now)
    name = factory.Faker("name")
    description = factory.Faker("text")
    price = Decimal("150000.00")
    available = True

    class Meta:
        model = Package


class PackagePurchaseFactory(factory.django.DjangoModelFactory):
    package = factory.SubFactory(PackageFactory)
    price = factory.SelfAttribute("package.price")

    class Meta:
        model = PackagePurchase
