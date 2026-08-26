from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.constants import UserType


User = get_user_model()


class UserSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=UserType.choices)
