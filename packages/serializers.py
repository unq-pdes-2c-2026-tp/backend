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
    class Meta:
        model = Hotel
        fields = ("id", "name", "description", "city", "photo")


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
