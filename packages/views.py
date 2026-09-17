from rest_framework import mixins
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
    GenericViewSet,
)

from packages.filters import (
    AgencyFilterSet,
    HotelFilterSet,
)
from packages.models import (
    Agency,
    Hotel,
    PackagePurchase,
)
from packages.serializers import (
    AgencySerializer,
    HotelSerializer,
    PackagePurchaseSerializer,
)
from users.permissions import (
    AdminPermission,
    EndUserPermission,
)


class AgencyViewSet(ModelViewSet):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    filterset_class = AgencyFilterSet

    def get_permissions(self):
        base_permissions = super().get_permissions()

        if self.action in ("create", "update", "partial_update", "destroy"):
            base_permissions.append(AdminPermission())

        return base_permissions


class HotelViewSet(ReadOnlyModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    filterset_class = HotelFilterSet


class PackagePurchaseViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = PackagePurchase.objects.select_related("package", "user").all()
    serializer_class = PackagePurchaseSerializer

    def get_permissions(self):
        base_permissions = super().get_permissions()

        if self.action == "create":
            base_permissions.append(EndUserPermission())

        return base_permissions

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
