"""/api/duyurular/ (A2 kabul: API taslakları döndürmüyor; K-23: izin verilmeyen alan dönmüyor)."""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Rol
from apps.duyurular import servisler
from apps.duyurular.models import Etiket
from apps.onay import akis

pytestmark = pytest.mark.django_db
LISTE = reverse("api_duyurular")


@pytest.fixture
def yk(kullanici_yap):
    return kullanici_yap(Rol.YONETIM_KURULU, "Başkan", email="yk@ornek.org")


def yayimla(yk, **veri):
    d = servisler.kaydet_duyuru(
        yk, {"baslik": "Başlık", "etiket": Etiket.DUYURU, "ozet": "Özet", "govde": "<p>Metin</p>", **veri}
    )
    akis.onaya_gonder(yk, d)
    return akis.onayla(yk, d)


def test_yalnizca_yayindakiler_doner(client, yk):
    yayinda = yayimla(yk, baslik="Yayında")
    servisler.kaydet_duyuru(yk, {"baslik": "Taslak", "ozet": "x", "govde": "<p>x</p>"})
    bekleyen = servisler.kaydet_duyuru(yk, {"baslik": "Bekleyen", "ozet": "x", "govde": "<p>x</p>"})
    akis.onaya_gonder(yk, bekleyen)
    kaldirilan = yayimla(yk, baslik="Kaldırılan")
    servisler.yayindan_kaldir(yk, kaldirilan)

    yanit = client.get(LISTE)
    assert yanit.status_code == 200 and yanit["Content-Type"] == "application/json"
    assert [d["slug"] for d in yanit.json()] == [yayinda.slug]
    for d in (bekleyen, kaldirilan):
        assert client.get(reverse("api_duyuru", args=[d.slug])).status_code == 404
    assert client.get(reverse("api_duyuru", args=[yayinda.slug])).json()["baslik"] == "Yayında"


def test_yalnizca_izinli_alanlar_doner(client, yk):
    zaman = timezone.now() + timedelta(days=3)
    d = servisler.kaydet_duyuru(
        yk,
        {"baslik": "Atölye", "etiket": Etiket.ETKINLIK, "ozet": "Özet", "govde": "<p>x</p>"},
        etkinlik_bilgisi={"baslangic": zaman, "yer": "[Salon]"},
    )
    akis.onaya_gonder(yk, d)
    akis.onayla(yk, d)
    veri = client.get(LISTE).json()[0]
    assert set(veri) == {"slug", "baslik", "etiket", "ozet", "govde", "yayin_tarihi", "etkinlik"}
    assert veri["etiket"] == "Etkinlik"
    assert set(veri["etkinlik"]) == {"baslangic", "bitis", "yer", "cevrim_ici", "harita_baglantisi"}
    assert veri["etkinlik"]["yer"] == "[Salon]"
    metin = str(veri)
    assert "yk@ornek.org" not in metin and "onay" not in metin


def test_etkinliksiz_duyuruda_etkinlik_bos_ve_siralama(client, yk):
    eski = yayimla(yk, baslik="Eski", etiket=Etiket.CAGRI)
    yeni = yayimla(yk, baslik="Yeni")
    veri = client.get(LISTE).json()
    assert [d["slug"] for d in veri] == [yeni.slug, eski.slug]
    assert veri[1]["etiket"] == "Çağrı" and veri[1]["etkinlik"] is None


def test_yazma_istekleri_reddedilir(client, yk):
    d = yayimla(yk)
    for adres in (LISTE, reverse("api_duyuru", args=[d.slug])):
        for yontem in (client.post, client.put, client.patch, client.delete):
            assert yontem(adres, data={}, content_type="application/json").status_code == 405


def test_giris_yapmis_kullaniciya_da_taslak_donmez(client, yk, tam_giris):
    servisler.kaydet_duyuru(yk, {"baslik": "Taslak", "ozet": "x", "govde": "<p>x</p>"})
    tam_giris(yk)
    assert client.get(LISTE).json() == []


def test_govde_temizlenmis_html(client, yk):
    yayimla(yk, govde='<p>a</p><script>alert(1)</script><a href="javascript:x">b</a>')
    assert client.get(LISTE).json()[0]["govde"] == '<p>a</p><a rel="noopener noreferrer">b</a>'
