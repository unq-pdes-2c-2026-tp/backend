from rest_framework import routers

from packages.views import AgencyViewSet

router = routers.SimpleRouter()
router.register(r"agencies", AgencyViewSet)

urlpatterns = router.urls
