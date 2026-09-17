import requests
from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from packages.models import (
    Agency,
    Hotel,
    Package,
    PackagePurchase,
)


class AgencySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=50, validators=[UniqueValidator(queryset=Agency.objects.all())]
    )

    class Meta:
        model = Agency
        fields = ("id", "name")


class HotelSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = ("id", "name", "description", "city", "photo")

    def get_photo(self, hotel):
        if not hotel.photo:
            return None
        request = self.context.get("request")
        return (
            request.build_absolute_uri(hotel.photo.url) if request else hotel.photo.url
        )


class PackageSerializer(serializers.ModelSerializer):
    agency = serializers.PrimaryKeyRelatedField(read_only=True)
    agency_name = serializers.CharField(source="agency.name", read_only=True)
    hotel_name = serializers.CharField(source="hotel.name", read_only=True)
    hotel_photo = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = (
            "id",
            "name",
            "description",
            "price",
            "available",
            "agency",
            "agency_name",
            "hotel",
            "hotel_name",
            "hotel_photo",
            "origin",
            "outbound_flight_id",
            "outbound_flight_date",
            "return_flight_id",
            "return_flight_date",
        )
        read_only_fields = ("id", "agency", "agency_name", "hotel_name", "hotel_photo")

    def get_hotel_photo(self, package):
        if not package.hotel.photo:
            return None
        request = self.context.get("request")
        return (
            request.build_absolute_uri(package.hotel.photo.url)
            if request
            else package.hotel.photo.url
        )

    def validate(self, attrs):
        if attrs["return_flight_date"] <= attrs["outbound_flight_date"]:
            raise serializers.ValidationError(
                {"return_flight_date": "Debe ser posterior a la fecha de ida."}
            )

        try:
            outbound_response = requests.get(
                f"{settings.FLIGHTS_API_URL}{attrs['outbound_flight_id']}/",
                timeout=5,
            )
            return_response = requests.get(
                f"{settings.FLIGHTS_API_URL}{attrs['return_flight_id']}/",
                timeout=5,
            )
            outbound_response.raise_for_status()
            return_response.raise_for_status()
        except requests.RequestException as error:
            raise serializers.ValidationError(
                {
                    "outbound_flight_id": "No se pudieron validar los vuelos seleccionados."
                }
            ) from error

        outbound_flight = outbound_response.json()
        return_flight = return_response.json()
        if outbound_flight.get("origen") != return_flight.get(
            "destino"
        ) or outbound_flight.get("destino") != return_flight.get("origen"):
            raise serializers.ValidationError(
                {
                    "return_flight_id": (
                        "El vuelo de vuelta debe salir del destino de ida "
                        "y llegar al origen de ida."
                    )
                }
            )
        return attrs


class PackagePurchaseSerializer(serializers.ModelSerializer):
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PackagePurchase
        fields = (
            "id",
            "package",
            "user",
            "datetime",
            "price",
        )
        read_only_fields = ("id", "user", "datetime", "price")

    def create(self, validated_data):
        validated_data["price"] = validated_data["package"].price
        return super().create(validated_data)
