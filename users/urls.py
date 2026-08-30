from django.urls import path
from rest_framework import routers

from users.views import UserViewSet, LoginView

router = routers.SimpleRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("login/", LoginView.as_view()),
] + router.urls
