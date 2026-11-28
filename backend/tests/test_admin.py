"""Django Admin'in özel kullanıcı modeliyle çalıştığını ve yetkisiz erişimi engellediğini denetler."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from conftest import dogrulanmis_giris

Kullanici = get_user_model()
SIFRE = "uzun-ve-guclu-sifre-2026"


@pytest.fixture
def teknik(client):
    k = Kullanici.objects.create_superuser(email="teknik@ornek.org", password=SIFRE)
    dogrulanmis_giris(client, k)
    return k


@pytest.mark.django_db
def test_giris_yapmamis_kisi_admine_giremez(client):
    yanit = client.get(reverse("admin:accounts_kullanici_changelist"))
    assert yanit.status_code == 302
    assert reverse("admin:login") in yanit["Location"]


@pytest.mark.django_db
def test_yetkisiz_kullanici_admine_giremez(client):
    k = Kullanici.objects.create_user(email="editor@ornek.org", password=SIFRE)
    client.force_login(k)
    yanit = client.get(reverse("admin:accounts_kullanici_changelist"))
    assert yanit.status_code == 302


@pytest.mark.django_db
def test_admin_kullanici_listesi_ve_duzenleme_acilir(client, teknik):
    assert client.get(reverse("admin:accounts_kullanici_changelist")).status_code == 200
    assert client.get(reverse("admin:accounts_kullanici_change", args=[teknik.pk])).status_code == 200


@pytest.mark.django_db
def test_admin_eposta_ile_kullanici_ekler(client, teknik):
    yanit = client.post(
        reverse("admin:accounts_kullanici_add"),
        {"email": "Yeni.Kisi@Firat.edu.tr", "password1": SIFRE, "password2": SIFRE, "usable_password": "true"},
    )
    assert yanit.status_code == 302, yanit.content.decode()[:2000]
    assert Kullanici.objects.filter(email__iexact="yeni.kisi@firat.edu.tr").exists()


@pytest.mark.django_db
def test_admin_kisa_sifreyi_reddeder(client, teknik):
    yanit = client.post(
        reverse("admin:accounts_kullanici_add"),
        {"email": "kisa@ornek.org", "password1": "Kisa-123", "password2": "Kisa-123", "usable_password": "true"},
    )
    assert yanit.status_code == 200
    assert not Kullanici.objects.filter(email="kisa@ornek.org").exists()


@pytest.mark.django_db
def test_2fa_dogrulanmamis_superuser_admine_giremez(client):
    k = Kullanici.objects.create_superuser(email="su@ornek.org", password=SIFRE)
    client.force_login(k)
    yanit = client.get(reverse("admin:accounts_kullanici_changelist"))
    assert yanit.status_code == 302
    assert reverse("admin:login") in yanit["Location"]
