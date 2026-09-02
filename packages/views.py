from rest_framework.viewsets import ModelViewSet

from packages.models import Agency
from packages.serializers import AgencySerializer
from users.permissions import AdminPermission


class AgencyViewSet(ModelViewSet):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer

    def get_permissions(self):
        base_permissions = super().get_permissions()

        if self.action in ("create", "update", "partial_update", "destroy"):
            base_permissions.append(AdminPermission())

        return base_permissions
