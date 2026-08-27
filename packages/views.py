from rest_framework.viewsets import ModelViewSet

from packages.models import Agency
from packages.serializers import AgencySerializer


class AgencyViewSet(ModelViewSet):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
