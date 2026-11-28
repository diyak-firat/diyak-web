import pytest
from django.contrib.auth import authenticate, get_user_model
from django.test import RequestFactory
from django.db import IntegrityError

Kullanici = get_user_model()


@pytest.mark.django_db
def test_eposta_ile_kullanici_olusur_ve_kullanici_adi_yoktur():
    k = Kullanici.objects.create_user(email="ad.soyad@firat.edu.tr", password="uzun-ve-guclu-sifre-2026")
    assert k.email == "ad.soyad@firat.edu.tr"
    assert not hasattr(k, "username") or k.username is None
    assert k.is_staff is False and k.is_superuser is False
    assert k.check_password("uzun-ve-guclu-sifre-2026")


@pytest.mark.django_db
def test_eposta_kucuk_harfe_cevrilir_ve_benzersizdir():
    Kullanici.objects.create_user(email="Ad.Soyad@Firat.EDU.tr", password="x" * 12)
    assert Kullanici.objects.filter(email="ad.soyad@firat.edu.tr").exists()
    with pytest.raises(IntegrityError):
        Kullanici.objects.create_user(email="AD.SOYAD@firat.edu.tr", password="x" * 12)


@pytest.mark.django_db
def test_eposta_ve_sifreyle_giris_yapilir():
    Kullanici.objects.create_user(email="giris@ornek.org", password="uzun-ve-guclu-sifre-2026")
    assert authenticate(RequestFactory().post("/giris/"), email="giris@ornek.org", password="uzun-ve-guclu-sifre-2026") is not None
    assert authenticate(RequestFactory().post("/giris/"), email="giris@ornek.org", password="yanlis-sifre-0000") is None


@pytest.mark.django_db
def test_giriste_eposta_buyuk_kucuk_harf_duyarsiz():
    Kullanici.objects.create_user(email="giris@ornek.org", password="uzun-ve-guclu-sifre-2026")
    assert authenticate(RequestFactory().post("/giris/"), email="Giris@Ornek.ORG", password="uzun-ve-guclu-sifre-2026") is not None


@pytest.mark.django_db
def test_eposta_zorunludur():
    with pytest.raises(ValueError):
        Kullanici.objects.create_user(email="", password="x" * 12)


@pytest.mark.django_db
def test_super_kullanici_bayraklari():
    k = Kullanici.objects.create_superuser(email="teknik@ornek.org", password="x" * 12)
    assert k.is_staff and k.is_superuser
    with pytest.raises(ValueError):
        Kullanici.objects.create_superuser(email="t2@ornek.org", password="x" * 12, is_superuser=False)
