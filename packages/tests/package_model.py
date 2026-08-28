import os

import django
from django.apps import apps
from django.db import models


def test_package_model_has_expected_fields():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ctv.settings.ci")
    django.setup()

    package_model = apps.get_model("packages", "Package")

    assert hasattr(package_model, "agency_id")
    assert hasattr(package_model, "hotel_id")
    assert isinstance(
        package_model._meta.get_field("outbound_flight_id"), models.PositiveIntegerField
    )
    assert isinstance(
        package_model._meta.get_field("return_flight_id"), models.PositiveIntegerField
    )
    assert hasattr(package_model, "name")
    assert hasattr(package_model, "description")
    assert hasattr(package_model, "price")
