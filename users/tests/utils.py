import io

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


def make_image():
    image_file = io.BytesIO()
    image = Image.new("RGB", (100, 100), "white")
    image.save(image_file, "jpeg")
    image_file.seek(0)

    django_file = SimpleUploadedFile(
        name="test_image.jpg", content=image_file.read(), content_type="image/jpeg"
    )
    return django_file
