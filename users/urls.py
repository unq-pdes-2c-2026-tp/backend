from django.urls import path
from rest_framework import routers

from users.views import UserViewSet, LoginView, LogoutView

router = routers.SimpleRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
] + router.urls
