"""Etkinlik (PANEL.md §6). Duyurulara ve (A4) kayıt formlarına bağlanır."""

from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

# Yalnızca Google Maps adresleri (kullanıcı kararı, 2026-11-28): gömülü harita ve API anahtarı yok.
HARITA_ALANLARI = {
    ("google.com", "/maps"),
    ("www.google.com", "/maps"),
    ("google.com.tr", "/maps"),
    ("www.google.com.tr", "/maps"),
    ("maps.google.com", "/"),
    ("maps.app.goo.gl", "/"),
    ("goo.gl", "/maps"),
}


def harita_baglantisi_dogrula(adres: str) -> None:
    parca = urlparse(adres or "")
    yol = parca.path or "/"
    if parca.scheme != "https" or not any(
        parca.netloc.lower() == alan and yol.startswith(onek) for alan, onek in HARITA_ALANLARI
    ):
        raise ValidationError(
            "Google Haritalar'daki “Paylaş” bağlantısını yapıştırın (https://maps.app.goo.gl/… "
            "veya https://www.google.com/maps/…)."
        )


class Etkinlik(models.Model):
    ad = models.CharField("ad", max_length=200)
    aciklama = models.CharField("kısa açıklama", max_length=300, blank=True)
    baslangic = models.DateTimeField("başlangıç")
    bitis = models.DateTimeField("bitiş", null=True, blank=True)
    yer = models.CharField("yer", max_length=200)
    cevrim_ici = models.BooleanField("çevrim içi", default=False)
    harita_baglantisi = models.URLField(
        "harita bağlantısı", max_length=500, blank=True, validators=[harita_baglantisi_dogrula],
        help_text="İsteğe bağlı. Google Haritalar'da yeri bulup “Paylaş”tan kopyaladığınız bağlantı.",
    )
    olusturan = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    olusturma = models.DateTimeField(auto_now_add=True)
    guncelleme = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "etkinlik"
        verbose_name_plural = "etkinlikler"
        ordering = ["-baslangic"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(bitis__isnull=True) | models.Q(bitis__gte=models.F("baslangic")),
                name="etkinlik_bitis_baslangictan_once_olamaz",
            )
        ]

    def __str__(self) -> str:
        return f"{self.ad} · {self.baslangic:%d.%m.%Y}"
