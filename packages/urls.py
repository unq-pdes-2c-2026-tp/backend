from django.urls import path
from rest_framework import routers

from packages.views import AgencyViewSet, FlightListView, HotelViewSet, PackageViewSet

router = routers.SimpleRouter()
router.register(r"agencies", AgencyViewSet)
router.register(r"hotels", HotelViewSet)
router.register(r"packages", PackageViewSet)

urlpatterns = [path("flights/", FlightListView.as_view(), name="flight-list")] + router.urls
