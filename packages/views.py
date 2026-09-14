from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from packages.filters import AgencyFilterSet, HotelFilterSet
from packages.models import Agency, Hotel
from packages.serializers import AgencySerializer, HotelSerializer
from users.permissions import AdminPermission


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
