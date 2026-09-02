from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from packages.models import Agency
from packages.serializers import AgencySerializer
from users.permissions import AdminPermission


class AgencyViewSet(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer

    def get_permissions(self):
        base_permissions = super().get_permissions()

        if self.action == "create":
            base_permissions.append(AdminPermission())

        return base_permissions
