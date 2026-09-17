from django.urls import path
from rest_framework import routers

from packages.views import (
    AgencyViewSet,
    FlightListView,
    HotelViewSet,
    PackageViewSet,
    PackagePurchaseViewSet,
)

router = routers.SimpleRouter()
router.register(r"agencies", AgencyViewSet)
router.register(r"hotels", HotelViewSet)
router.register(r"packages", PackageViewSet)
router.register(r"purchases", PackagePurchaseViewSet)


urlpatterns = [
    path("flights/", FlightListView.as_view(), name="flight-list")
] + router.urls
