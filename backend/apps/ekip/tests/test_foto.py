"""Fotoğraf işleme: EXIF silinir, kare ve 800 piksel, yalnızca görüntü kabul edilir (A3 kabul)."""

import io

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.ekip.foto import foto_isle

from .conftest import resim


def exif_konumlu(yon=1):
    exif = Image.Exif()
    exif[0x0112] = yon  # Orientation
    exif[0x010F] = "Telefon Markasi"  # Make
    exif[0x8825] = {1: "N", 2: (38.0, 40.0, 0.0), 3: "E", 4: (39.0, 13.0, 0.0)}  # GPS
    return exif


def ac(icerik):
    return Image.open(io.BytesIO(icerik.read()))


def test_exif_ve_konum_silinir_kare_800():
    cikti = foto_isle(resim(exif=exif_konumlu()))
    g = ac(cikti)
    assert g.format == "JPEG" and g.size == (800, 800)
    assert len(g.getexif()) == 0
    assert cikti.name.endswith(".jpg") and cikti.name != "foto.jpg"


def test_dondurme_bilgisi_uygulanir():
    # 1200x600 yatay, EXIF "90° döndür" → dikey görüntü; kare kırpma ortadan yapılır, hata olmaz.
    g = ac(foto_isle(resim(boyut=(1200, 600), exif=exif_konumlu(yon=6))))
    assert g.size == (800, 800) and len(g.getexif()) == 0


@pytest.mark.parametrize("bicim", ["PNG", "WEBP"])
def test_png_ve_webp_kabul_edilir_jpeg_olur(bicim):
    assert ac(foto_isle(resim(bicim=bicim))).format == "JPEG"


def test_gif_reddedilir():
    with pytest.raises(ValidationError, match="JPEG, PNG veya WebP"):
        foto_isle(resim(bicim="GIF"))


@pytest.mark.parametrize(
    "icerik",
    [b"<?php echo 1; ?>", b"%PDF-1.4 sahte", b"\xff\xd8\xff\xe0 bozuk jpeg", b"<svg onload=alert(1)></svg>"],
)
def test_goruntu_olmayan_dosya_reddedilir(icerik):
    with pytest.raises(ValidationError):
        foto_isle(SimpleUploadedFile("foto.jpg", icerik, content_type="image/jpeg"))


def test_cok_buyuk_dosya_reddedilir():
    dosya = SimpleUploadedFile("foto.jpg", b"x" * (10 * 1024 * 1024 + 1), content_type="image/jpeg")
    with pytest.raises(ValidationError, match="10 MB"):
        foto_isle(dosya)


def test_cok_fazla_pikselli_goruntu_reddedilir():
    tampon = io.BytesIO()
    Image.new("1", (8000, 8000)).save(tampon, format="PNG")  # 64 milyon piksel, küçük dosya
    with pytest.raises(ValidationError):
        foto_isle(SimpleUploadedFile("foto.png", tampon.getvalue(), content_type="image/png"))
