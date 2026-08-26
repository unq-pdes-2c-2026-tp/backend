from django.contrib.auth import get_user_model
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from users.managers import UserManager
from users.serializers import UserSerializer

User = get_user_model()


class UserViewSet(CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        manager: UserManager = User.objects
        manager.create_user(**serializer.validated_data)
