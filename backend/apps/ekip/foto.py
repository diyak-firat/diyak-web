"""Ekip fotoğrafı işleme (PANEL.md §9, K-27).

Yüklenen dosya Pillow ile açılıp doğrulanır, telefonun döndürme bilgisine göre çevrilir, ortadan
kare kırpılır, 800×800'e küçültülür ve **yeniden kodlanarak** JPEG olarak kaydedilir. Yeniden
kodlama EXIF'i (konum, cihaz bilgisi) ve dosyaya gizlenmiş her türlü ek veriyi atar. Kaydedilen
her fotoğraf yeni bir dosyadır; var olan dosyanın üzerine yazılmaz (onaylı sürüm eski fotoğrafı
göstermeye devam edebilsin diye).
"""

import io
import uuid

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageOps, UnidentifiedImageError

EN_FAZLA_BAYT = 10 * 1024 * 1024
EN_FAZLA_PIKSEL = 50_000_000  # sıkıştırma bombasına karşı
IZINLI_BICIMLER = {"JPEG", "PNG", "WEBP"}
BOYUT = 800


def foto_isle(dosya) -> ContentFile:
    if dosya.size > EN_FAZLA_BAYT:
        raise ValidationError("Fotoğraf en fazla 10 MB olabilir.")
    try:
        with Image.open(dosya) as goruntu:
            goruntu.verify()
        dosya.seek(0)
        goruntu = Image.open(dosya)
        if goruntu.format not in IZINLI_BICIMLER:
            raise ValidationError("Fotoğraf JPEG, PNG veya WebP olmalı.")
        if goruntu.width * goruntu.height > EN_FAZLA_PIKSEL:
            raise ValidationError("Fotoğraf çok büyük; daha küçük bir görüntü yükleyin.")
        goruntu = ImageOps.exif_transpose(goruntu)
        goruntu = ImageOps.fit(goruntu.convert("RGB"), (BOYUT, BOYUT), Image.Resampling.LANCZOS)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, SyntaxError) as hata:
        raise ValidationError("Dosya okunamadı; geçerli bir fotoğraf yükleyin.") from hata
    cikti = io.BytesIO()
    goruntu.save(cikti, format="JPEG", quality=85, optimize=True, progressive=True)
    return ContentFile(cikti.getvalue(), name=f"{uuid.uuid4().hex}.jpg")
