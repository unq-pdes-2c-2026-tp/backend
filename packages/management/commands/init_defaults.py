from dataclasses import dataclass
from datetime import datetime
from random import choice, randint

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command
from django.db import transaction

from packages.flight_api_client import FlightAPIClient
from packages.models import Agency, Hotel, Package, City
from users.constants import UserType

User = get_user_model()


@dataclass
class Flight:
    id: int
    datetime: datetime


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        self._create_agencies()
        agency = Agency.objects.first()
        if agency is not None:
            self._create_users(agency=agency)

        call_command("create_hotels")
        self._create_packages(agency)

    def _create_packages(self, agency: Agency | None):
        hotels = Hotel.objects.select_related("city")
        cities: set[City] = {hotel.city for hotel in hotels}

        flights = self._get_flights_for_cities(list(cities))

        origin_by_destination: dict[City, City] = dict(flights.keys())

        packages = []
        package_name_templates = [
            "Tu viaje soñado a {city_name}",
            "{city_name} te espera con las mejores aventuras",
            "El destino del verano: {city_name}",
            "{city_name}: una experiencia inolvidable",
            "Descubrí los encantos de {city_name}",
            "Viví momentos únicos en {city_name}",
            "{city_name}, el lugar perfecto para tu próxima escapada",
            "Explorá todo lo que {city_name} tiene para ofrecer",
        ]

        for hotel in hotels:
            name = choice(package_name_templates).format(city_name=hotel.city.name)
            origin_city = origin_by_destination[hotel.city]
            destination_city = hotel.city
            package = Package(
                name=name,
                hotel=hotel,
                agency=agency,
                origin=origin_by_destination[hotel.city],
                price=randint(150_000, 450_000),
                description="",
                outbound_flight_id=flights[origin_city, destination_city].id,
                outbound_flight_date=flights[origin_city, destination_city].datetime,
                return_flight_id=flights[destination_city, origin_city].id,
                return_flight_date=flights[destination_city, origin_city].datetime,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Creando paquete de {package.origin.name} a {hotel.city.name} en el hotel {hotel.name}"
                )
            )
            packages.append(package)

        Package.objects.bulk_create(packages)
        self.stdout.write(self.style.SUCCESS(f"Se crearon {len(packages)} paquetes"))

    def _create_agencies(self):
        agency_names = [
            {"name": "Despegar"},
            {"name": "Turismo City"},
            {"name": "Juliá Tours"},
            {"name": "Costa Azul Viajes"},
            {"name": "Argentinian Explorer"},
            {"name": "Tangol"},
            {"name": "Biblos Travel"},
            {"name": "Eves"},
            {"name": "Pezzati Viajes"},
            {"name": "ANDA Travel"},
        ]

        agencies = [Agency(**agency) for agency in agency_names]
        Agency.objects.bulk_create(agencies)
        self.stdout.write(
            self.style.SUCCESS(f"Se crearon {len(agency_names)} agencias")
        )

    def _create_users(self, agency: Agency):
        users = [
            {
                "email": "admin@gmail.com",
                "user_type": UserType.ADMIN,
                "password": "admin",
                "agency": None,
            },
            {
                "email": "user@gmail.com",
                "user_type": UserType.END_USER,
                "password": "user",
                "agency": None,
            },
            {
                "email": "agency@gmail.com",
                "user_type": UserType.AGENCY,
                "password": "agency",
                "agency": agency,
            },
        ]
        for user_data in users:
            password = user_data.pop("password")
            user = User(**user_data)
            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(f"Se creó el usuario {user_data['email']}")
            )

    def _get_flights_for_cities(
        self, cities: list[City]
    ) -> dict[tuple[City, City], Flight]:
        client = FlightAPIClient()
        flights = client.get_flights("")["results"]

        city_by_name = {city.name.lower(): city for city in cities}

        result: dict[tuple[City, City], Flight] = dict()

        for flight in flights:
            origin_name = flight["origen"].lower()
            destination_name = flight["destino"].lower()
            if origin_name in city_by_name and destination_name in city_by_name:
                origin_city = city_by_name[origin_name]
                destination_city = city_by_name[destination_name]

                result[(origin_city, destination_city)] = self._make_flight(flight)
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"No se encontró ciudad con nombre {flight['origen']} o {flight['destino']}"
                    )
                )

        return result

    def _make_flight(self, flight):
        return Flight(
            id=flight["id"],
            datetime=datetime.strptime(
                f"{flight['fecha']}T{flight['hora']}-03:00", "%Y-%m-%dT%H:%M:%S%z"
            ),
        )
