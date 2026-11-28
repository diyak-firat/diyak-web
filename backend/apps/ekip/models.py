"""Ekip sayfası (PANEL.md §6, §8).

Kişiler ve gruplar panelde serbestçe düzenlenen **çalışma kopyasıdır**; sitede görünmez. Onaya
gönderilince o anki hali (yalnızca yayın onayı olan kişiler ve sitede görünecek alanlar) bir
``Degisiklik`` kaydına donmuş olarak yazılır. Yönetim Kurulu onaylayınca site ve ``/api/ekip/`` bu
donmuş hali gösterir. Böylece onaydan sonra yapılan düzenlemeler, yeniden onaylanana kadar sitede
görünmez.
"""

from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

# Kişi kartındaki bağlantılar: anahtar → sitede görünen ad. Yalnızca https adresleri.
BAGLANTI_TURLERI = {
    "orcid": "ORCID",
    "linkedin": "LinkedIn",
    "github": "GitHub",
    "scholar": "Google Scholar",
    "scopus": "Scopus",
    "dergipark": "DergiPark",
    "wos": "Web of Science",
    "yok": "YÖK Akademik",
    "web": "Kişisel sayfa",
}


def baglantilari_dogrula(deger) -> None:
    if not isinstance(deger, dict):
        raise ValidationError("Bağlantılar geçersiz.")
    for anahtar, adres in deger.items():
        if anahtar not in BAGLANTI_TURLERI:
            raise ValidationError(f"Bilinmeyen bağlantı türü: {anahtar}")
        parca = urlparse(str(adres))
        if parca.scheme != "https" or not parca.netloc or len(str(adres)) > 300:
            raise ValidationError(f"{BAGLANTI_TURLERI[anahtar]} adresi https:// ile başlamalı.")


class Donem(models.Model):
    ad = models.CharField("ad", max_length=40, unique=True, help_text="ör. 2026–2027")
    baslangic = models.DateField("başlangıç")
    bitis = models.DateField("bitiş")
    aktif = models.BooleanField("aktif", default=False)
    olusturma = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "dönem"
        verbose_name_plural = "dönemler"
        ordering = ["-baslangic"]
        constraints = [
            models.UniqueConstraint(fields=["aktif"], condition=models.Q(aktif=True), name="tek_aktif_donem"),
            models.CheckConstraint(condition=models.Q(bitis__gte=models.F("baslangic")), name="donem_bitis_sonra"),
        ]

    def __str__(self) -> str:
        return self.ad


class GrupTuru(models.TextChoices):
    DANISMAN = "danisman", "Akademik Danışman"
    YONETIM = "yonetim", "Yönetim"
    BIRIM = "birim", "Birim"


class Grup(models.Model):
    donem = models.ForeignKey(Donem, on_delete=models.CASCADE, related_name="gruplar")
    ad = models.CharField("ad", max_length=120)
    tur = models.CharField("tür", max_length=20, choices=GrupTuru.choices, default=GrupTuru.BIRIM)
    sira = models.PositiveIntegerField("sıra", default=0)

    class Meta:
        verbose_name = "grup"
        verbose_name_plural = "gruplar"
        ordering = ["donem", "sira", "pk"]

    def __str__(self) -> str:
        return f"{self.donem} · {self.ad}"


class Kisi(models.Model):
    grup = models.ForeignKey(Grup, on_delete=models.CASCADE, related_name="kisiler")
    ad = models.CharField("ad soyad", max_length=150)
    gorev = models.CharField("görev", max_length=100, help_text="ör. Başkan, Birim Sorumlusu, Üye")
    birim = models.CharField(
        "fakülte / bölüm", max_length=200, blank=True, help_text="Akademik danışman için, ör. Mühendislik Fakültesi"
    )
    eposta = models.EmailField("e-posta", blank=True)
    foto = models.FileField("fotoğraf", upload_to="ekip/", blank=True)
    sira = models.PositiveIntegerField("sıra", default=0)
    baglantilar = models.JSONField("bağlantılar", default=dict, blank=True, validators=[baglantilari_dogrula])
    yayin_onayi_tarihi = models.DateField(
        "yazılı yayın onayı tarihi",
        null=True,
        blank=True,
        help_text="Kişinin bilgilerinin yayımlanmasına yazılı onay verdiği gün. Boşsa kişi sitede görünmez (KVKK).",
    )
    kullanici = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    guncelleme = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "kişi"
        verbose_name_plural = "kişiler"
        ordering = ["grup", "sira", "pk"]

    def __str__(self) -> str:
        return self.ad


class DegisiklikDurumu(models.TextChoices):
    TASLAK = "taslak", "Düzeltme istendi"
    ONAY_BEKLIYOR = "onay_bekliyor", "Onay bekliyor"
    YAYINDA = "yayinda", "Yayında"
    ESKI = "eski", "Önceki yayın"


class Degisiklik(models.Model):
    """Ekip sayfasının onaya gönderilen donmuş hali. En son onaylanan sitede görünür."""

    donem = models.ForeignKey(Donem, on_delete=models.PROTECT, related_name="degisiklikler")
    durum = models.CharField(max_length=20, choices=DegisiklikDurumu.choices, default=DegisiklikDurumu.TASLAK)
    ozet = models.CharField("değişiklik özeti", max_length=300)
    veri = models.JSONField("yayımlanacak içerik", default=dict)
    olusturan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    onaylayan = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    onay_notu = models.TextField(blank=True)
    yayin_tarihi = models.DateTimeField(null=True, blank=True)
    olusturma = models.DateTimeField(auto_now_add=True)
    guncelleme = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ekip değişikliği"
        verbose_name_plural = "ekip değişiklikleri"
        ordering = ["-olusturma"]

    def __str__(self) -> str:
        return f"{self.donem} · {self.ozet}"

    def eksikler(self) -> list[str]:
        eksik = []
        if not self.ozet.strip():
            eksik.append("Değişikliği bir cümleyle özetleyin.")
        if not self.veri.get("gruplar"):
            eksik.append("Yayımlanacak grup yok.")
        return eksik

    def onaylaninca(self, simdi) -> None:
        Degisiklik.objects.filter(durum=DegisiklikDurumu.YAYINDA).exclude(pk=self.pk).update(
            durum=DegisiklikDurumu.ESKI
        )
        self.durum = DegisiklikDurumu.YAYINDA
        self.yayin_tarihi = simdi
