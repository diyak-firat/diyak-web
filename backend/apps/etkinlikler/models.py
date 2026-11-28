"""Etkinlik (PANEL.md §6). A2'de duyurulara bağlanır; etkinlik ekranları ve kayıt formları A4'te."""

from django.conf import settings
from django.db import models


class Etkinlik(models.Model):
    ad = models.CharField("ad", max_length=200)
    aciklama = models.CharField("kısa açıklama", max_length=300, blank=True)
    baslangic = models.DateTimeField("başlangıç")
    bitis = models.DateTimeField("bitiş", null=True, blank=True)
    yer = models.CharField("yer", max_length=200)
    cevrim_ici = models.BooleanField("çevrim içi", default=False)
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
