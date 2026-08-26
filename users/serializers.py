from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.constants import UserType


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=UserType.choices)

    class Meta:
        model = User
        fields = ("name", "email", "password", "user_type", "agency")

    def validate(self, data):
        user_type = data.get("user_type", None)
        if data.get("agency", None) is None and user_type == UserType.AGENCY.value:
            raise serializers.ValidationError(
                {"agency": ["This field is required for user type agency."]}
            )

        return data
