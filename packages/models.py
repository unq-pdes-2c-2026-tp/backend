from django.db import models


class Agency(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Package(models.Model):
    agency = models.ForeignKey(
        Agency,
        on_delete=models.PROTECT,
        related_name="packages",
    )
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.PROTECT,
        related_name="packages",
    )
    outbound_flight_id = models.PositiveIntegerField()
    return_flight_id = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name
