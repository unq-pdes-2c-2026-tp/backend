from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext_lazy as _
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
        fields = (
            "id",
            "name",
            "email",
            "password",
            "user_type",
            "agency",
            "profile_picture",
        )

    def validate(self, data):
        user_type = data.get("user_type", None)
        if data.get("agency", None) is None and user_type == UserType.AGENCY.value:
            raise serializers.ValidationError(
                {"agency": ["This field is required for user type agency."]}
            )

        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class UserLoginSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50, read_only=True)
    email = serializers.EmailField(read_only=True)
    user_type = serializers.ChoiceField(choices=UserType.choices, read_only=True)

    class Meta:
        model = User
        fields = ("id", "name", "email", "user_type", "agency")
