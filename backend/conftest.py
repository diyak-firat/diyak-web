"""Ortak test yardımcıları. Yalnızca sahte veri kullanılır."""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.models import GOREV_BASKAN, Rol, RolAtamasi

SIFRE = "uzun-ve-guclu-sifre-2026"


@pytest.fixture
def kullanici_yap(db):
    sayac = {"n": 0}

    def yap(rol: str | None = None, gorev_adi: str = "", bitis=None, baslangic=None, **alanlar):
        sayac["n"] += 1
        alanlar.setdefault("email", f"kisi{sayac['n']}@ornek.org")
        k = get_user_model().objects.create_user(password=SIFRE, **alanlar)
        if rol:
            bugun = timezone.localdate()
            RolAtamasi.objects.create(
                kullanici=k,
                rol=rol,
                gorev_adi=gorev_adi,
                baslangic=baslangic or bugun - timedelta(days=30),
                bitis=bitis or bugun + timedelta(days=180),
            )
        return k

    return yap


@pytest.fixture
def baskan(kullanici_yap):
    return kullanici_yap(Rol.YONETIM_KURULU, GOREV_BASKAN, email="baskan@ornek.org")


@pytest.fixture
def teknik(kullanici_yap):
    return kullanici_yap(Rol.TEKNIK, email="teknik@ornek.org")


@pytest.fixture
def donem_sonu():
    return timezone.localdate() + timedelta(days=200)
