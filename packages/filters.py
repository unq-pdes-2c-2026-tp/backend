from django.db.models import Q
from django_filters import rest_framework as filters

from packages.models import Agency, Hotel


class AgencyFilterSet(filters.FilterSet):
    search = filters.CharFilter(
        method="search_func", help_text="Filter agencies by name substring"
    )

    class Meta:
        model = Agency
        fields = ()

    def search_func(self, qs, name, value):
        return qs.filter(name__icontains=value)


class HotelFilterSet(filters.FilterSet):
    search = filters.CharFilter(
        method="search_func",
        help_text="Filter hotels by name, description or city name substring",
    )

    class Meta:
        model = Hotel
        fields = ()

    def search_func(self, qs, name, value):
        search_filter = (
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(city__name__icontains=value)
        )
        return qs.filter(search_filter)
