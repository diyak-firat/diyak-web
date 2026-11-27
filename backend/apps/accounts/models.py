"""Kullanıcı modeli. Giriş kimliği e-postadır; kullanıcı adı yoktur (PANEL.md §6).

Roller, davetler ve 2FA A1 aşamasında bu uygulamaya eklenecek.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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
