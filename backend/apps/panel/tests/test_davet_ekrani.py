"""Davet bağlantısıyla hesap açma ekranı (PANEL.md §3)."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts import servisler
from apps.accounts.models import Rol, RolAtamasi
from conftest import SIFRE

pytestmark = pytest.mark.django_db
KABUL = reverse("panel:davet_kabul")


@pytest.fixture
def davet(baskan, donem_sonu):
    return servisler.davet_olustur(baskan, "davetli@ornek.org", Rol.EDITOR, donem_sonu, "Medya Birimi")


def bilgiler(sifre=SIFRE, sifre2=None):
    return {"ad": "Deniz", "soyad": "Yılmaz", "sifre1": sifre, "sifre2": sifre2 or sifre}


def test_bagdaki_belirtec_adres_cubugundan_silinir(client, davet):
    _, token = davet
    yanit = client.get(reverse("panel:davet", args=[token]))
    assert yanit["Location"] == KABUL
    sayfa = client.get(KABUL)
    assert sayfa.status_code == 200
    icerik = sayfa.content.decode()
    assert "davetli@ornek.org" in icerik and "Medya Birimi" in icerik and token not in icerik


def test_davet_kabul_hesabi_acar_ve_2fa_kurulumuna_gonderir(client, davet):
    _, token = davet
    client.get(reverse("panel:davet", args=[token]))
    yanit = client.post(KABUL, bilgiler())
    assert yanit["Location"] == reverse("panel:kurulum")
    k = get_user_model().objects.get(email="davetli@ornek.org")
    assert (k.first_name, k.last_name) == ("Deniz", "Yılmaz")
    assert RolAtamasi.objects.filter(kullanici=k, rol=Rol.EDITOR).exists()
    # Hesap açıldı ama 2FA kurulmadan panel açılmaz.
    assert client.get(reverse("panel:ana"))["Location"] == reverse("panel:kurulum")
    # Bağlantı ikinci kez kullanılamaz.
    assert client.get(reverse("panel:davet", args=[token])).status_code == 404


@pytest.mark.parametrize("token", ["yok", "a" * 43])
def test_gecersiz_belirtec_404(client, db, token):
    yanit = client.get(reverse("panel:davet", args=[token]))
    assert yanit.status_code == 404
    assert "geçersiz" in yanit.content.decode()


def test_oturumda_davet_yoksa_kabul_ekrani_acilmaz(client, db):
    assert client.get(KABUL).status_code == 404
    assert client.post(KABUL, bilgiler()).status_code == 404
    assert not get_user_model().objects.filter(email="davetli@ornek.org").exists()


@pytest.mark.parametrize("sifre,sifre2", [("kisa", None), ("123456789012345", None), (SIFRE, SIFRE + "x")])
def test_zayif_veya_eslesmeyen_sifre_reddedilir(client, davet, sifre, sifre2):
    _, token = davet
    client.get(reverse("panel:davet", args=[token]))
    yanit = client.post(KABUL, bilgiler(sifre, sifre2))
    assert yanit.status_code == 200
    assert not get_user_model().objects.filter(email="davetli@ornek.org").exists()


def test_girisli_kisi_davet_acinca_oturumu_kapanir(client, davet, kullanici_yap, tam_giris):
    tam_giris(kullanici_yap(Rol.EDITOR))
    _, token = davet
    client.get(reverse("panel:davet", args=[token]))
    assert not client.session.get("_auth_user_id")
