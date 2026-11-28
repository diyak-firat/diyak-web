import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


@pytest.fixture(autouse=True)
def gecici_medya(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"
    return settings.MEDIA_ROOT


def resim(bicim="JPEG", boyut=(1200, 900), exif=None, renk=(200, 30, 30)) -> SimpleUploadedFile:
    tampon = io.BytesIO()
    goruntu = Image.new("RGB", boyut, renk)
    kwargs = {"exif": exif} if exif is not None else {}
    goruntu.save(tampon, format=bicim, **kwargs)
    uzanti = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp", "GIF": "gif"}[bicim]
    return SimpleUploadedFile(f"foto.{uzanti}", tampon.getvalue(), content_type=f"image/{uzanti}")
