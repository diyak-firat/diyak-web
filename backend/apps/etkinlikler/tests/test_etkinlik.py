from datetime import timedelta

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from apps.accounts.models import Rol
from apps.denetim.models import Eylem, IslemKaydi
from apps.duyurular import servisler as duyuru_servisi
from apps.etkinlikler import servisler
from apps.etkinlikler.models import Etkinlik, harita_baglantisi_dogrula
from apps.onay import akis

pytestmark = pytest.mark.django_db
ZAMAN = timezone.now() + timedelta(days=10)


@pytest.fixture
def editor(kullanici_yap):
    return kullanici_yap(Rol.EDITOR)


@pytest.fixture
def yk(kullanici_yap):
    return kullanici_yap(Rol.YONETIM_KURULU, "Sayman")


def veri(**ek):
    return {"ad": "NLP atölyesi", "baslangic": ZAMAN, "yer": "[Salon]", **ek}


@pytest.mark.parametrize(
    "adres",
    [
        "https://maps.app.goo.gl/AbC123",
        "https://www.google.com/maps/place/F%C4%B1rat+%C3%9Cniversitesi/@38.67,39.19,17z",
        "https://google.com/maps?q=38.67,39.19",
        "https://goo.gl/maps/xyz",
        "https://maps.google.com/?q=Elazig",
        "https://www.google.com.tr/maps/place/x",
    ],
)
def test_google_haritalar_kabul(adres):
    harita_baglantisi_dogrula(adres)


@pytest.mark.parametrize(
    "adres",
    [
        "http://maps.app.goo.gl/AbC123",
        "https://kotu.example/maps",
        "https://maps.app.goo.gl.kotu.example/x",
        "https://www.google.com/search?q=x",
        "https://goo.gl/AbC",
        "javascript:alert(1)",
        "https://evil.com/?https://maps.app.goo.gl/",
        "https://www.openstreetmap.org/#map=17/38.6/39.1",
    ],
)
def test_baska_adresler_reddedilir(adres):
    with pytest.raises(ValidationError):
        harita_baglantisi_dogrula(adres)


def test_editor_olusturur_ve_duzenler(editor):
    e = servisler.kaydet_etkinlik(editor, veri(harita_baglantisi="https://maps.app.goo.gl/x"))
    assert e.olusturan == editor and e.harita_baglantisi
    servisler.kaydet_etkinlik(editor, {"yer": "[Salon 2]"}, e)
    e.refresh_from_db()
    assert e.yer == "[Salon 2]"
    with pytest.raises(ValidationError):
        servisler.kaydet_etkinlik(editor, {"harita_baglantisi": "https://kotu.example/x"}, e)
    with pytest.raises(ValidationError):
        servisler.kaydet_etkinlik(editor, {"bitis": ZAMAN - timedelta(hours=1)}, e)


@pytest.mark.parametrize("rol", [Rol.DANISMAN, Rol.TEKNIK, None])
def test_yetkisizler(kullanici_yap, editor, rol):
    k = kullanici_yap(rol)
    e = servisler.kaydet_etkinlik(editor, veri())
    with pytest.raises(PermissionDenied):
        servisler.kaydet_etkinlik(k, veri())
    with pytest.raises(PermissionDenied):
        servisler.kaydet_etkinlik(k, {"yer": "x"}, e)
    with pytest.raises(PermissionDenied):
        servisler.sil(k, e)


def test_yayindaki_duyuruya_bagli_etkinligi_yalnizca_yk_degistirir(editor, yk):
    e = servisler.kaydet_etkinlik(editor, veri())
    d = duyuru_servisi.kaydet_duyuru(
        editor, {"baslik": "Atölye", "etiket": "etkinlik", "ozet": "ö", "govde": "<p>x</p>"}, etkinlik=e
    )
    assert d.etkinlik == e
    akis.onaya_gonder(editor, d)
    with pytest.raises(PermissionDenied):  # onay bekliyorken de
        servisler.kaydet_etkinlik(editor, {"yer": "Sessiz değişiklik"}, e)
    akis.onayla(yk, d)
    with pytest.raises(PermissionDenied):
        servisler.kaydet_etkinlik(editor, {"yer": "Sessiz değişiklik"}, e)
    servisler.kaydet_etkinlik(yk, {"yer": "[Yeni salon]"}, e)
    e.refresh_from_db()
    assert e.yer == "[Yeni salon]"
    assert IslemKaydi.objects.filter(eylem=Eylem.YAYIMLAMA, nesne_turu="etkinlikler.etkinlik").exists()


def test_duyuruya_bagli_etkinlik_silinemez(editor):
    e = servisler.kaydet_etkinlik(editor, veri())
    duyuru_servisi.kaydet_duyuru(editor, {"baslik": "A", "etiket": "etkinlik", "ozet": "ö", "govde": "<p>x</p>"}, etkinlik=e)
    with pytest.raises(ValidationError):
        servisler.sil(editor, e)
    bos = servisler.kaydet_etkinlik(editor, veri(ad="Boş"))
    servisler.sil(editor, bos)
    assert not Etkinlik.objects.filter(pk=bos.pk).exists()
