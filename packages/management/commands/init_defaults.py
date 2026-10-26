from django.core.management import BaseCommand

from packages.models import Agency


class Command(BaseCommand):
    def handle(self, *args, **options):
        agencies = [Agency(name=f"agencia {i}") for i in range(10)]
        Agency.objects.bulk_create(agencies)

        self.stdout.write(self.style.SUCCESS("Se crearon 10 agencias"))
