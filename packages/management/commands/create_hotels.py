import requests

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from packages.models import City, Hotel


HOTELS_ARGENTINA = {
    "Four Seasons Hotel Buenos Aires": {
        "city": "Buenos Aires",
        "description": (
            "Hotel de lujo que combina una elegante mansión histórica "
            "con un moderno edificio, ofreciendo una experiencia "
            "exclusiva en el barrio de Recoleta."
        ),
        "photo_url": (
            "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/2c/01/31/3f/pool.jpg?w=900&h=500&s=1"
        ),
    },
    "Faena Hotel Buenos Aires": {
        "city": "Buenos Aires",
        "description": (
            "Hotel de estilo contemporáneo y artístico ubicado en "
            "Puerto Madero, conocido por su diseño llamativo, "
            "gastronomía y propuesta de entretenimiento."
        ),
        "photo_url": (
            "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/1b/4a/bc/0e/vista-desde-el-parque.jpg?w=900&h=500&s=1"
        ),
    },
    "Llao Llao Resort, Golf-Spa": {
        "city": "San Carlos de Bariloche",
        "description": (
            "Icónico resort patagónico situado entre lagos y montañas, "
            "con vistas espectaculares, campo de golf, spa y una amplia "
            "variedad de actividades."
        ),
        "photo_url": (
            "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0d/80/96/ec/llao-llao-hotel-and-resort.jpg?w=900&h=500&s=1"
        ),
    },
    "El Casco Art Hotel": {
        "city": "San Carlos de Bariloche",
        "description": (
            "Hotel boutique frente al lago Nahuel Huapi que combina "
            "arquitectura patagónica, arte y confort en un entorno "
            "natural privilegiado."
        ),
        "photo_url": (
            "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/04/b0/9f/07/el-casco-art-hotel.jpg?w=900&h=-1&s=1"
        ),
    },
    "The Vines of Mendoza": {
        "city": "Mendoza",
        "description": (
            "Exclusivo resort en el corazón de la región vitivinícola "
            "de Mendoza, rodeado de viñedos y con una propuesta "
            "centrada en el vino, la gastronomía y la naturaleza."
        ),
        "photo_url": (
            "https://vinesofmendoza.com/wp-content/uploads/2025/05/0002-768x605.jpg"
        ),
    },
    "Gran Meliá Iguazú": {
        "city": "Puerto Iguazú",
        "description": (
            "Resort de lujo ubicado dentro del Parque Nacional Iguazú, "
            "con vistas a la selva y una ubicación privilegiada cerca "
            "de las Cataratas del Iguazú."
        ),
        "photo_url": (
            "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/2a/c9/99/53/caption.jpg?w=900&h=-1&s=1"
        ),
    },
    "Loi Suites Iguazú Hotel": {
        "city": "Puerto Iguazú",
        "description": (
            "Resort rodeado por la selva misionera que ofrece una "
            "experiencia de descanso y naturaleza, a pocos kilómetros "
            "de las Cataratas del Iguazú."
        ),
        "photo_url": (
            "https://lh3.googleusercontent.com/proxy/mNdTkY2L_2eNd5u8joSGIblzoAb1sqvhX0GS3EqT5FbhH7OKfCB83Oqw8ot3Tza-2-F1YC3MKkjKI5EMue1KrREggLbaRvfvOSAGOLt2-7hobKxEsNCbgbg4Bc_cOCX7SDQJLOWzq7z1vZcD7jUf4AQsq-Xxi3I=s680-w680-h510-rw"
        ),
    },
}


class Command(BaseCommand):
    help = "Creates cities and hotels"

    def handle(self, *args, **options):
        with requests.Session() as session:
            for hotel_name, data in HOTELS_ARGENTINA.items():
                city, _ = City.objects.get_or_create(
                    name=data["city"],
                )

                hotel, created = Hotel.objects.get_or_create(
                    name=hotel_name,
                    defaults={
                        "city": city,
                        "description": data["description"],
                    },
                )

                if hotel.photo and hotel.photo.storage.exists(hotel.photo.name):
                    self.stdout.write(f"Photo already exists: {hotel_name}")
                    continue

                try:
                    response = session.get(
                        data["photo_url"],
                        timeout=10,
                    )
                    response.raise_for_status()

                    hotel.photo.save(
                        f"{hotel_name}.jpg",
                        ContentFile(response.content),
                        save=True,
                    )

                    self.stdout.write(
                        self.style.SUCCESS(f"Created hotel: {hotel_name}")
                    )

                except requests.RequestException as exc:
                    self.stdout.write(
                        self.style.ERROR(f"Error downloading {hotel_name}: {exc}")
                    )
