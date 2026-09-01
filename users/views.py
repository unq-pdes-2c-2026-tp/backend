from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_404_NOT_FOUND,
    HTTP_204_NO_CONTENT,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from rest_framework.viewsets import ModelViewSet

from users.managers import UserManager
from users.serializers import (
    UserSerializer,
    LoginSerializer,
    UserLoginSerializer,
    ProfilePictureSerializer,
)

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        manager: UserManager = User.objects
        manager.create_user(**serializer.validated_data)

    @action(
        detail=False,
        methods=["post", "delete"],
        url_path="profile-picture",
        permission_classes=[IsAuthenticated],
        parser_classes=[MultiPartParser],
    )
    def profile_picture(self, request):
        if request.method == "POST":
            serializer = ProfilePictureSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = request.user
            profile_picture = serializer.validated_data["profile_picture"]
            user.profile_picture = profile_picture

            user.save(update_fields=["profile_picture"])

            return Response(
                {
                    "profile_picture": user.profile_picture.url
                    if user.profile_picture
                    else None
                }
            )

        if request.method == "DELETE":
            user = request.user
            if user.profile_picture:
                user.profile_picture.delete(save=False)
                user.profile_picture = None
                user.save(update_fields=["profile_picture"])
                return Response(status=HTTP_204_NO_CONTENT)
            else:
                return Response(status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_405_METHOD_NOT_ALLOWED)


class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            UserLoginSerializer(user).data, headers={"Authentication": token.key}
        )
