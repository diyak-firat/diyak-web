"""Duyuru (PANEL.md §6). Sitedeki gündem gönderisinin karşılığıdır.

Gövde her kayıtta ``html_temizle`` ile temizlenir; hangi yoldan gelirse gelsin (panel, Admin,
aktarım komutu) temizlenmemiş HTML veritabanına girmez.
"""

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from .temizle import html_temizle

_TURKCE = str.maketrans({"ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ı": "i", "İ": "i", "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u", "â": "a", "î": "i", "û": "u"})


def turkce_slug(metin: str) -> str:
    return slugify(metin.translate(_TURKCE))[:80].strip("-") or "duyuru"


class Etiket(models.TextChoices):
    ETKINLIK = "etkinlik", "Etkinlik"
    DUYURU = "duyuru", "Duyuru"
    CAGRI = "cagri", "Çağrı"
    YAYIN = "yayin", "Yayın"


class Durum(models.TextChoices):
    TASLAK = "taslak", "Taslak"
    ONAY_BEKLIYOR = "onay_bekliyor", "Onay bekliyor"
    YAYINDA = "yayinda", "Yayında"
    KALDIRILDI = "kaldirildi", "Yayından kaldırıldı"


class Duyuru(models.Model):
    baslik = models.CharField("başlık", max_length=140)
    slug = models.SlugField("adres", max_length=90, unique=True, editable=False)
    etiket = models.CharField("etiket", max_length=20, choices=Etiket.choices, default=Etiket.DUYURU)
    ozet = models.CharField("özet", max_length=300)
    govde = models.TextField("metin", blank=True)
    etkinlik = models.ForeignKey(
        "etkinlikler.Etkinlik",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="duyurular",
        verbose_name="bağlı etkinlik",
    )
    durum = models.CharField("durum", max_length=20, choices=Durum.choices, default=Durum.TASLAK, db_index=True)
    yayin_tarihi = models.DateTimeField("yayın tarihi", null=True, blank=True)
    olusturan = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+", verbose_name="hazırlayan"
    )
    onaylayan = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    onay_notu = models.TextField("onay notu", blank=True)
    olusturma = models.DateTimeField(auto_now_add=True)
    guncelleme = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "duyuru"
        verbose_name_plural = "duyurular"
        ordering = ["-guncelleme"]

    def __str__(self) -> str:
        return self.baslik

    def save(self, *args, **kwargs):
        self.govde = html_temizle(self.govde)
        if not self.slug:
            self.slug = self._benzersiz_slug()
        super().save(*args, **kwargs)

    def _benzersiz_slug(self) -> str:
        temel = turkce_slug(self.baslik)
        aday, n = temel, 2
        while Duyuru.objects.filter(slug=aday).exclude(pk=self.pk).exists():
            aday, n = f"{temel}-{n}", n + 1
        return aday

    def eksikler(self) -> list[str]:
        """Onaya gönderilmeden önce tamamlanması gerekenler (boşsa gönderilebilir)."""
        eksik = []
        if not self.baslik.strip():
            eksik.append("Başlık boş.")
        if not self.ozet.strip():
            eksik.append("Özet boş.")
        if not self.govde.strip():
            eksik.append("Metin boş.")
        if self.etiket == Etiket.ETKINLIK and self.etkinlik_id is None:
            eksik.append("Etkinlik etiketli duyurunun etkinlik zamanı ve yeri girilmeli.")
        return eksik

    def onaylaninca(self, simdi) -> None:
        """Onay akışının son adımı: yayımla. İlk yayın tarihi korunur."""
        self.durum = Durum.YAYINDA
        if self.yayin_tarihi is None:
            self.yayin_tarihi = simdi
