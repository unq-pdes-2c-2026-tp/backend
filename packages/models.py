from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower


class Agency(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        constraints = [UniqueConstraint(Lower("name"), name="city_name_lower_unique")]


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    photo = models.ImageField(null=True)


class Package(models.Model):
    agency = models.ForeignKey(
        Agency, on_delete=models.CASCADE, related_name="packages"
    )
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="packages")
    outbound_flight_id = models.PositiveIntegerField()
    outbound_flight_date = models.DateTimeField()
    return_flight_id = models.PositiveIntegerField()
    return_flight_date = models.DateTimeField()
    origin = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Cuando se haga una venta, en la respuesta nos dicen si queda disponibilidad
    # y updateamos el campo
    available = models.BooleanField(default=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name


class PackageFavorite(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)


class PackagePurchase(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class PackageReview(models.Model):
    package_purchase = models.ForeignKey(PackagePurchase, on_delete=models.CASCADE)

    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    review = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now_add=True)
