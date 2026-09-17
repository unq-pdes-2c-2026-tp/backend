from datetime import date

import requests
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from packages.filters import AgencyFilterSet, HotelFilterSet
from packages.models import Agency, Hotel, Package
from packages.serializers import AgencySerializer, HotelSerializer, PackageSerializer
from users.permissions import AdminPermission, AgencyPermission


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
                settings.FLIGHTS_API_URL,
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
