from functools import reduce

from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import serializers

from packages.models import Agency, Hotel, Package


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


class PackageFilterSet(filters.FilterSet):
    agency_id = filters.CharFilter(method="filter_by_agency")
    search = filters.CharFilter(
        method="search_func", help_text="Filter packages by keyword"
    )

    class Meta:
        model = Package
        fields = ()

    def filter_by_agency(self, qs, name, value):
        try:
            int(value)
        except ValueError:
            raise serializers.ValidationError(f"Invalid filter value: {value}")
        return qs.filter(agency_id=value)

    def search_func(self, qs, name, value):
        included_fields = ("name", "description", "agency__name", "hotel__name")
        condition = reduce(
            lambda acc, field: acc | Q(**{f"{field}__icontains": value}),
            included_fields,
            Q(),
        )
        return qs.filter(condition)
