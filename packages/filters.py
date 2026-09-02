from django_filters import rest_framework as filters

from packages.models import Agency


class AgencyFilterSet(filters.FilterSet):
    search = filters.CharFilter(method="search_func")

    class Meta:
        model = Agency
        fields = ()

    def search_func(self, qs, name, value):
        return qs.filter(name__icontains=value)
