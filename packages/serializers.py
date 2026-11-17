import requests
from django.db import transaction
from requests import Response
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from packages.flight_api_client import FlightAPIClient
from packages.models import (
    Agency,
    Hotel,
    Package,
    PackagePurchase,
    PackageFavorite,
    PackageReview,
    City,
)
from users.serializers import UserLiteSerializer


class AgencySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=50, validators=[UniqueValidator(queryset=Agency.objects.all())]
    )

    class Meta:
        model = Agency
        fields = ("id", "name")


class AgencyDetailedSerializer(serializers.ModelSerializer):
    total_revenue = serializers.DecimalField(max_digits=20, decimal_places=2)
    avg_score = serializers.DecimalField(max_digits=3, decimal_places=1)

    class Meta:
        model = Agency
        fields = (
            "id",
            "name",
            "total_revenue",
            "avg_score",
        )


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
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
    avg_score = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)

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
            "avg_score",
            "reviews_count",
        )
        read_only_fields = (
            "id",
            "agency",
            "agency_name",
            "hotel_name",
            "hotel_photo",
            "avg_score",
            "reviews_count",
        )

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
        if self._get_field(attrs, "return_flight_date") <= self._get_field(
            attrs, "outbound_flight_date"
        ):
            raise serializers.ValidationError(
                {"return_flight_date": "Debe ser posterior a la fecha de ida."}
            )

        try:
            flight_api_client = FlightAPIClient()
            outbound_flight = self._validate_flight_id(
                flight_api_client, attrs, "outbound_flight_id"
            )
            return_flight = self._validate_flight_id(
                flight_api_client, attrs, "return_flight_id"
            )
        except requests.RequestException as error:
            raise serializers.ValidationError(
                {
                    "outbound_flight_id": "No se pudieron validar los vuelos seleccionados."
                }
            ) from error
        outbound_flight = outbound_flight or dict()
        return_flight = return_flight or dict()

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

    def _validate_flight_id(
        self, flight_api_client: FlightAPIClient, attrs, flight_id_field
    ) -> Response | None:
        response = None
        if flight_id_field in attrs:
            response = flight_api_client.get_flight(attrs[flight_id_field])

        return response

    def _get_field(self, data, field_name):
        return data.get(
            field_name,
            getattr(self.instance, field_name) if self.instance is not None else None,
        )


class PackageAdminSerializer(PackageSerializer):
    agency = serializers.PrimaryKeyRelatedField(queryset=Agency.objects.all())

    class Meta(PackageSerializer.Meta):
        pass


class PackageReviewLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageReview
        fields = ("id", "score", "review", "datetime")


class PackagePurchaseSerializer(serializers.ModelSerializer):
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())
    package_detail = PackageSerializer(source="package", read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_detail = UserLiteSerializer(source="user", read_only=True)
    reviews = PackageReviewLiteSerializer(
        source="packagereview_set", many=True, read_only=True
    )

    class Meta:
        model = PackagePurchase
        fields = (
            "id",
            "package",
            "package_detail",
            "user",
            "user_detail",
            "datetime",
            "price",
            "reviews",
        )
        read_only_fields = (
            "id",
            "package_detail",
            "user",
            "user_detail",
            "datetime",
            "price",
            "reviews",
        )

    def to_representation(self, instance):
        if hasattr(instance, "package_avg_score"):
            instance.package.avg_score = instance.package_avg_score
        if hasattr(instance, "package_reviews_count"):
            instance.package.reviews_count = instance.package_reviews_count
        return super().to_representation(instance)

    def _buy_flight(
        self, flight_api_client: FlightAPIClient, flight_id, user_name, user_email
    ):
        try:
            flight_api_client.buy_flight(flight_id, user_name, user_email)
        except requests.RequestException as error:
            raise serializers.ValidationError(
                {"package": "No se pudo comunicar con el servicio de vuelos."}
            ) from error

    @transaction.atomic()
    def create(self, validated_data):
        package: Package = validated_data["package"]
        validated_data["price"] = package.price
        user = validated_data["user"]
        client = FlightAPIClient()
        # Compra vuelo de ida
        self._buy_flight(client, package.outbound_flight_id, user.name, user.email)
        # Compra vuelo de vuelta
        self._buy_flight(client, package.return_flight_id, user.name, user.email)

        return super().create(validated_data)


class SpenderSerializer(serializers.Serializer):
    user = UserLiteSerializer()
    total_spent = serializers.DecimalField(max_digits=20, decimal_places=2)


class TopCityByPurchasesSerializer(serializers.Serializer):
    city = CitySerializer()
    total_purchases = serializers.IntegerField()


class TopCityByReviewsSerializer(serializers.Serializer):
    city = CitySerializer()
    avg_reviews = serializers.DecimalField(max_digits=20, decimal_places=2)


class TopAgencyByRevenueSerializer(serializers.Serializer):
    agency = AgencySerializer()
    total_revenue = serializers.DecimalField(max_digits=20, decimal_places=2)


class PackageFavoriteSerializer(serializers.ModelSerializer):
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PackageFavorite
        fields = (
            "id",
            "package",
            "user",
            "datetime",
        )
        read_only_fields = ("id", "user", "datetime")

    def validate(self, attrs):
        request = self.context.get("request")
        package = attrs.get("package")

        if (
            request
            and package
            and PackageFavorite.objects.filter(
                user=request.user, package=package
            ).exists()
        ):
            raise serializers.ValidationError(
                {"package": "Este paquete ya se encuentra en favoritos."}
            )

        return attrs


class PackageReviewSerializer(serializers.ModelSerializer):
    package_purchase = serializers.PrimaryKeyRelatedField(
        queryset=PackagePurchase.objects.all()
    )
    package_id = serializers.IntegerField(
        source="package_purchase.package_id", read_only=True
    )
    package_name = serializers.CharField(
        source="package_purchase.package.name", read_only=True
    )
    user_detail = UserLiteSerializer(source="package_purchase.user", read_only=True)

    class Meta:
        model = PackageReview
        fields = (
            "id",
            "package_purchase",
            "package_id",
            "package_name",
            "user_detail",
            "score",
            "review",
            "datetime",
        )
        read_only_fields = (
            "id",
            "package_id",
            "package_name",
            "user_detail",
            "datetime",
        )

    def validate_package_purchase(self, package_purchase):
        request = self.context.get("request")
        if request and package_purchase.user != request.user:
            raise serializers.ValidationError(
                "Solo puedes dejar reseñas sobre tus propias compras."
            )

        # Evitar duplicados
        qs = PackageReview.objects.filter(package_purchase=package_purchase)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Esta compra ya tiene una reseña registrada."
            )

        return package_purchase

    def update(self, instance, validated_data):
        # Evita que al editar se cambie la compra asociada
        validated_data.pop("package_purchase", None)
        return super().update(instance, validated_data)
