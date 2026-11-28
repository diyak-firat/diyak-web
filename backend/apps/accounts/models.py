"""Hesaplar: kullanıcı, dönemlik rol atamaları ve davetler (PANEL.md §3, §4, §6).

Giriş kimliği e-postadır; kullanıcı adı yoktur. Panel yetkileri yalnızca etkin rol
atamalarından gelir; ``is_staff`` / ``is_superuser`` yalnızca Django Admin içindir.
"""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class KullaniciYoneticisi(BaseUserManager["Kullanici"]):
    use_in_migrations = True

    def _olustur(self, email: str, password: str | None, **alanlar) -> "Kullanici":
        if not email:
            raise ValueError("E-posta zorunludur.")
        # E-posta büyük/küçük harf duyarsız tutulur: Ad@Firat.edu.tr ile ad@firat.edu.tr aynı hesaptır.
        email = self.normalize_email(email).lower()
        kullanici = self.model(email=email, **alanlar)
        kullanici.set_password(password)
        kullanici.save(using=self._db)
        return kullanici

    def get_by_natural_key(self, email: str) -> "Kullanici":
        # Girişte de büyük/küçük harf ayrımı yapılmaz.
        return self.get(email__iexact=email)

    def create_user(self, email: str, password: str | None = None, **alanlar) -> "Kullanici":
        alanlar.setdefault("is_staff", False)
        alanlar.setdefault("is_superuser", False)
        return self._olustur(email, password, **alanlar)

    def create_superuser(self, email: str, password: str | None = None, **alanlar) -> "Kullanici":
        alanlar.setdefault("is_staff", True)
        alanlar.setdefault("is_superuser", True)
        if alanlar.get("is_staff") is not True or alanlar.get("is_superuser") is not True:
            raise ValueError("Süper kullanıcıda is_staff ve is_superuser True olmalıdır.")
        return self._olustur(email, password, **alanlar)


class Kullanici(AbstractUser):
    username = None  # type: ignore[assignment]
    email = models.EmailField("e-posta", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = KullaniciYoneticisi()  # type: ignore[misc]

    class Meta:
        verbose_name = "kullanıcı"
        verbose_name_plural = "kullanıcılar"
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email


class Rol(models.TextChoices):
    YONETIM_KURULU = "yonetim_kurulu", "Yönetim Kurulu"
    EDITOR = "editor", "Editör"
    DANISMAN = "danisman", "Danışman"
    TEKNIK = "teknik", "Teknik sorumlu"


# Davet ve rol atama yetkisi bu görev adlarından birini taşıyan etkin Yönetim Kurulu
# atamasından gelir (PANEL.md §4). Panel bu adları seçenek olarak sunar; elle yazılmaz.
GOREV_BASKAN = "Başkan"
GOREV_BASKAN_YARDIMCISI = "Başkan Yardımcısı"
ATAMA_YETKILI_GOREVLER = (GOREV_BASKAN, GOREV_BASKAN_YARDIMCISI)


class RolAtamasiQuerySet(models.QuerySet["RolAtamasi"]):
    def etkin(self, gun=None) -> "RolAtamasiQuerySet":
        """Bugün (veya verilen günde) yetki veren atamalar. Bitiş günü dahildir.

        Kapatılmış (``is_active=False``) hesapların atamaları hiçbir zaman etkin sayılmaz.
        """
        gun = gun or timezone.localdate()
        return self.filter(baslangic__lte=gun, bitis__gte=gun, kullanici__is_active=True)


class RolAtamasi(models.Model):
    """Bir kullanıcıya belirli bir süre için verilen rol. Bitiş tarihi geçince yetki vermez."""

    kullanici = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rol_atamalari", verbose_name="kullanıcı"
    )
    rol = models.CharField("rol", max_length=20, choices=Rol.choices)
    gorev_adi = models.CharField(
        "görev adı", max_length=100, blank=True, help_text="ör. Başkan, Başkan Yardımcısı, İletişim Birimi"
    )
    baslangic = models.DateField("başlangıç", default=timezone.localdate)
    bitis = models.DateField("bitiş", help_text="Bu gün dahil etkindir; varsayılan olarak dönem sonu.")
    atayan = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="atayan",
    )
    olusturma = models.DateTimeField("oluşturma", auto_now_add=True)

    objects = RolAtamasiQuerySet.as_manager()

    class Meta:
        verbose_name = "rol ataması"
        verbose_name_plural = "rol atamaları"
        ordering = ["-bitis", "kullanici__email"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(bitis__gte=models.F("baslangic")), name="rol_bitis_baslangictan_once_olamaz"
            ),
        ]

    def __str__(self) -> str:
        gorev = f" ({self.gorev_adi})" if self.gorev_adi else ""
        return f"{self.kullanici} · {self.get_rol_display()}{gorev} · {self.bitis:%d.%m.%Y}"

    def etkin_mi(self, gun=None) -> bool:
        gun = gun or timezone.localdate()
        return self.kullanici.is_active and self.baslangic <= gun <= self.bitis


class Davet(models.Model):
    """Tek kullanımlık, 48 saat geçerli hesap açma daveti (PANEL.md §3).

    Bağlantıdaki belirtecin kendisi saklanmaz, yalnızca SHA-256 özeti saklanır: veritabanı
    okunsa bile açık davetler kullanılamaz.
    """

    GECERLILIK = timedelta(hours=48)

    eposta = models.EmailField("e-posta")
    rol = models.CharField("rol", max_length=20, choices=Rol.choices)
    gorev_adi = models.CharField("görev adı", max_length=100, blank=True)
    bitis = models.DateField("rolün bitişi")
    token_ozeti = models.CharField("belirteç özeti", max_length=64, unique=True, editable=False)
    davet_eden = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="davet eden",
    )
    olusturma = models.DateTimeField("oluşturma", auto_now_add=True)
    kullanildi = models.DateTimeField("kullanıldı", null=True, blank=True)

    class Meta:
        verbose_name = "davet"
        verbose_name_plural = "davetler"
        ordering = ["-olusturma"]

    def __str__(self) -> str:
        return f"{self.eposta} · {self.get_rol_display()}"

    @property
    def son_gecerlilik(self):
        return self.olusturma + self.GECERLILIK

    def gecerli_mi(self, simdi=None) -> bool:
        simdi = simdi or timezone.now()
        return self.kullanildi is None and simdi < self.son_gecerlilik
