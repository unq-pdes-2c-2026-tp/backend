from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from packages.models import Agency, Hotel


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
