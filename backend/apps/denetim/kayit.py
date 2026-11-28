"""İşlem kaydı yazmak için tek giriş noktası."""

from django.db import models

from .models import Eylem, IslemKaydi


def kaydet(
    eylem: Eylem,
    kullanici=None,
    nesne: models.Model | None = None,
    ayrinti: dict | None = None,
) -> IslemKaydi:
    """Bir işlemi kaydeder.

    ``ayrinti`` yalnızca kimlikler, roller, tarihler gibi kişisel olmayan bilgiler içerir.
    Anonim kullanıcı (giriş yapmamış) ``None`` olarak kaydedilir.
    """
    if kullanici is not None and not getattr(kullanici, "is_authenticated", False):
        kullanici = None
    return IslemKaydi.objects.create(
        kullanici=kullanici,
        eylem=eylem,
        nesne_turu=nesne._meta.label_lower if nesne is not None else "",
        nesne_id=str(nesne.pk) if nesne is not None else "",
        ayrinti=ayrinti or {},
    )
