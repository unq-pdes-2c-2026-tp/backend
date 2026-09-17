from rest_framework import routers

from packages.views import AgencyViewSet, HotelViewSet, PackagePurchaseViewSet

router = routers.SimpleRouter()
router.register(r"agencies", AgencyViewSet)
router.register(r"hotels", HotelViewSet)
router.register(r"purchases", PackagePurchaseViewSet)

urlpatterns = router.urls
