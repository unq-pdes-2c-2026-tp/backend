from datetime import date

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum, Value, Count, Avg, Q
from django.db.models.fields import DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import (
    serializers,
    status,
    mixins,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
    GenericViewSet,
)

from packages.aggregation import aggregate_package_purchase, aggregate_package_review
from packages.filters import (
    AgencyFilterSet,
    HotelFilterSet,
)
from packages.models import (
    Agency,
    Hotel,
    Package,
    PackagePurchase,
    City,
)
from packages.serializers import (
    AgencySerializer,
    HotelSerializer,
    PackageSerializer,
    PackagePurchaseSerializer,
    SpenderSerializer,
    TopCityByPurchasesSerializer,
    TopCityByReviewsSerializer,
    AgencyDetailedSerializer,
)
from users.permissions import (
    AdminPermission,
    AgencyPermission,
    EndUserPermission,
)

User = get_user_model()


class AgencyViewSet(ModelViewSet):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    filterset_class = AgencyFilterSet

    def get_permissions(self):
        base_permissions = super().get_permissions()

        if self.action in ("create", "update", "partial_update", "destroy"):
            base_permissions.append(AdminPermission())

        return base_permissions

    @action(
        methods=["get"],
        url_path="detailed",
        permission_classes=[IsAuthenticated, AdminPermission],
        detail=False,
    )
    def list_detailed(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        page = page or queryset
        agency_ids = [agency.id for agency in page]

        today = timezone.now()
        first_day_of_month = today.replace(day=1)
        revenue_by_id = (
            self.get_queryset()
            .filter(
                Q(
                    packages__packagepurchase__datetime__gte=first_day_of_month,
                    packages__packagepurchase__datetime__lte=today,
                )
                | Q(packages__isnull=True),
                id__in=agency_ids,
            )
            .values("id")
            .annotate(
                total_revenue=Coalesce(
                    Sum("packages__packagepurchase__price"),
                    Value(0.0),
                    output_field=DecimalField(),
                )
            )
        )

        revenue_by_id = {item["id"]: item["total_revenue"] for item in revenue_by_id}
        results = []
        for agency in page:
            results.append(
                {
                    "id": agency.id,
                    "name": agency.name,
                    "total_revenue": revenue_by_id.get(agency.id, 0),
                }
            )

        return Response(AgencyDetailedSerializer(results, many=True).data)


class HotelViewSet(ReadOnlyModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    filterset_class = HotelFilterSet


class PackageViewSet(ModelViewSet):
    queryset = Package.objects.select_related("agency", "hotel").all()
    serializer_class = PackageSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), AgencyPermission()]
        return super().get_permissions()

    def perform_create(self, serializer):
        if self.request.user.agency_id is None:
            raise serializers.ValidationError(
                {"agency": "El usuario agencia debe tener una agencia asociada."}
            )
        serializer.save(agency=self.request.user.agency)


class FlightListView(APIView):
    def get(self, request):
        try:
            response = requests.get(
                settings.FLIGHTS_API_URL + "vuelos/",
                params={"search": request.query_params.get("search", "")},
                timeout=5,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            return Response(
                {
                    "detail": "No se pudo consultar la API de vuelos.",
                    "error": str(error),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        payload = response.json()
        flights = (
            payload.get("results", payload) if isinstance(payload, dict) else payload
        )
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        try:
            date_from = date.fromisoformat(date_from) if date_from else None
            date_to = date.fromisoformat(date_to) if date_to else None
        except ValueError:
            return Response(
                {"detail": "Las fechas deben usar el formato YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if date_from or date_to:
            flights = [
                flight
                for flight in flights
                if (not date_from or date.fromisoformat(flight["fecha"]) >= date_from)
                and (not date_to or date.fromisoformat(flight["fecha"]) <= date_to)
            ]
        return Response(flights)


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

    @action(
        methods=["get"],
        detail=False,
        url_path="top-spenders",
        permission_classes=[IsAuthenticated, AdminPermission],
    )
    def top_spenders(self, request):
        result = aggregate_package_purchase(
            dimension_field="user",
            dimension_name="user",
            dimension_model=User,
            expression=Coalesce(Sum("price"), Value(0.0), output_field=DecimalField()),
            result_key="total_spent",
        )

        return Response(SpenderSerializer(result, many=True).data)

    @action(
        methods=["get"],
        detail=False,
        url_path="top-cities-by-purchases",
        permission_classes=[IsAuthenticated, AdminPermission],
    )
    def top_cities_by_purchases(self, request):
        result = aggregate_package_purchase(
            dimension_field="package__hotel__city",
            dimension_name="city",
            dimension_model=City,
            expression=Count("id"),
            result_key="total_purchases",
        )

        return Response(TopCityByPurchasesSerializer(result, many=True).data)

    @action(
        methods=["get"],
        detail=False,
        url_path="top-cities-by-reviews",
        permission_classes=[IsAuthenticated, AdminPermission],
    )
    def top_cities_by_reviews(self, request):
        result = aggregate_package_review(
            dimension_field="package_purchase__package__hotel__city",
            dimension_name="city",
            dimension_model=City,
            expression=Avg("score"),
            result_key="avg_reviews",
        )

        return Response(TopCityByReviewsSerializer(result, many=True).data)
