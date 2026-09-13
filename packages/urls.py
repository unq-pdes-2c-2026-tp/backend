from rest_framework import routers

from packages.views import AgencyViewSet, HotelViewSet

router = routers.SimpleRouter()
router.register(r"agencies", AgencyViewSet)
router.register(r"hotels", HotelViewSet)

urlpatterns = router.urls
