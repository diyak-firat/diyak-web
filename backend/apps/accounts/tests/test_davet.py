"""Davet ve rol atama işlemleri (PANEL.md §3, §4)."""

from datetime import timedelta

import pytest
from django.contrib.auth import authenticate, get_user_model
from django.test import RequestFactory
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from apps.accounts import servisler
from apps.accounts.models import Davet, Rol, RolAtamasi
from apps.denetim.models import Eylem, IslemKaydi

pytestmark = pytest.mark.django_db
SIFRE = "uzun-ve-guclu-sifre-2026"


def test_baskan_davet_eder_ve_kabul_hesap_ile_rol_acar(baskan, donem_sonu):
    davet, token = servisler.davet_olustur(baskan, "Yeni.Uye@Firat.edu.tr", Rol.EDITOR, donem_sonu, "İletişim Birimi")
    assert davet.eposta == "yeni.uye@firat.edu.tr"
    assert davet.token_ozeti != token and token not in davet.token_ozeti
    assert servisler.davet_bul(token) == davet

    k = servisler.daveti_kullan(token, SIFRE, "Ad", "Soyad")
    assert authenticate(RequestFactory().post("/giris/"), email="yeni.uye@firat.edu.tr", password=SIFRE) == k
    atama = RolAtamasi.objects.get(kullanici=k)
    assert (atama.rol, atama.gorev_adi, atama.bitis, atama.atayan) == (Rol.EDITOR, "İletişim Birimi", donem_sonu, baskan)
    assert servisler.davet_bul(token) is None


def test_davet_tek_kullanimliktir(baskan, donem_sonu):
    _, token = servisler.davet_olustur(baskan, "a@ornek.org", Rol.EDITOR, donem_sonu)
    servisler.daveti_kullan(token, SIFRE)
    with pytest.raises(ValidationError):
        servisler.daveti_kullan(token, SIFRE)


def test_davet_48_saat_sonra_gecersizdir(baskan, donem_sonu):
    davet, token = servisler.davet_olustur(baskan, "a@ornek.org", Rol.EDITOR, donem_sonu)
    Davet.objects.filter(pk=davet.pk).update(olusturma=timezone.now() - timedelta(hours=48, seconds=1))
    assert servisler.davet_bul(token) is None
    with pytest.raises(ValidationError):
        servisler.daveti_kullan(token, SIFRE)
    assert not get_user_model().objects.filter(email="a@ornek.org").exists()


@pytest.mark.parametrize("token", ["", "uydurma-belirtec"])
def test_olmayan_davet_kabul_edilmez(db, token):
    assert servisler.davet_bul(token) is None
    with pytest.raises(ValidationError):
        servisler.daveti_kullan(token, SIFRE)


def test_davette_zayif_sifre_reddedilir_ve_davet_acik_kalir(baskan, donem_sonu):
    _, token = servisler.davet_olustur(baskan, "a@ornek.org", Rol.EDITOR, donem_sonu)
    with pytest.raises(ValidationError):
        servisler.daveti_kullan(token, "kisa-sifre")
    assert servisler.davet_bul(token) is not None
    assert not get_user_model().objects.filter(email="a@ornek.org").exists()


def test_yeni_davet_eskisini_gecersiz_kilar(baskan, donem_sonu):
    _, eski = servisler.davet_olustur(baskan, "a@ornek.org", Rol.EDITOR, donem_sonu)
    _, yeni = servisler.davet_olustur(baskan, "A@ornek.org", Rol.DANISMAN, donem_sonu)
    assert servisler.davet_bul(eski) is None
    assert servisler.davet_bul(yeni) is not None


def test_var_olan_hesaba_davet_gonderilmez(baskan, donem_sonu):
    with pytest.raises(ValidationError):
        servisler.davet_olustur(baskan, "BASKAN@ornek.org", Rol.EDITOR, donem_sonu)


def test_gecmis_bitisle_davet_olmaz(baskan):
    with pytest.raises(ValidationError):
        servisler.davet_olustur(baskan, "a@ornek.org", Rol.EDITOR, timezone.localdate() - timedelta(days=1))


def test_gecersiz_rolle_davet_olmaz(baskan, donem_sonu):
    with pytest.raises(ValidationError):
        servisler.davet_olustur(baskan, "a@ornek.org", "baskan", donem_sonu)


@pytest.mark.parametrize("rol,gorev", [(Rol.EDITOR, ""), (Rol.YONETIM_KURULU, "Sayman"), (Rol.DANISMAN, "")])
def test_baskanlik_disi_davet_edemez(kullanici_yap, donem_sonu, rol, gorev):
    k = kullanici_yap(rol, gorev)
    with pytest.raises(PermissionDenied):
        servisler.davet_olustur(k, "a@ornek.org", Rol.EDITOR, donem_sonu)
    assert not Davet.objects.exists()


def test_suresi_dolmus_baskan_davet_edemez(kullanici_yap, donem_sonu):
    dun = timezone.localdate() - timedelta(days=1)
    k = kullanici_yap(Rol.YONETIM_KURULU, "Başkan", baslangic=dun - timedelta(days=300), bitis=dun)
    with pytest.raises(PermissionDenied):
        servisler.davet_olustur(k, "a@ornek.org", Rol.EDITOR, donem_sonu)


def test_baskan_teknik_davet_edemez_teknik_edebilir(baskan, teknik, donem_sonu):
    with pytest.raises(PermissionDenied):
        servisler.davet_olustur(baskan, "a@ornek.org", Rol.TEKNIK, donem_sonu)
    with pytest.raises(PermissionDenied):
        servisler.davet_olustur(teknik, "a@ornek.org", Rol.EDITOR, donem_sonu)
    servisler.davet_olustur(teknik, "a@ornek.org", Rol.TEKNIK, donem_sonu)


def test_rol_ata_ve_kaldir(baskan, kullanici_yap, donem_sonu):
    k = kullanici_yap()
    atama = servisler.rol_ata(baskan, k, Rol.DANISMAN, donem_sonu)
    assert atama.etkin_mi() and atama.atayan == baskan
    servisler.rol_kaldir(baskan, atama)
    assert not RolAtamasi.objects.filter(kullanici=k).exists()


def test_yetkisiz_rol_atayamaz_ve_kaldiramaz(kullanici_yap, baskan, donem_sonu):
    editor = kullanici_yap(Rol.EDITOR)
    hedef = kullanici_yap()
    with pytest.raises(PermissionDenied):
        servisler.rol_ata(editor, hedef, Rol.YONETIM_KURULU, donem_sonu)
    with pytest.raises(PermissionDenied):
        servisler.rol_ata(editor, editor, Rol.YONETIM_KURULU, donem_sonu, "Başkan")
    atama = servisler.rol_ata(baskan, hedef, Rol.EDITOR, donem_sonu)
    with pytest.raises(PermissionDenied):
        servisler.rol_kaldir(editor, atama)
    assert RolAtamasi.objects.filter(pk=atama.pk).exists()


def test_kapatilmis_hesaba_rol_atanmaz(baskan, kullanici_yap, donem_sonu):
    k = kullanici_yap(is_active=False)
    with pytest.raises(ValidationError):
        servisler.rol_ata(baskan, k, Rol.EDITOR, donem_sonu)


def test_islemler_kisisel_veri_olmadan_kayda_gecer(baskan, kullanici_yap, donem_sonu):
    davet, token = servisler.davet_olustur(baskan, "gizli.kisi@ornek.org", Rol.EDITOR, donem_sonu)
    yeni = servisler.daveti_kullan(token, SIFRE, "Gizli", "Kişi")
    atama = RolAtamasi.objects.get(kullanici=yeni)
    servisler.rol_kaldir(baskan, atama)

    kayitlar = list(IslemKaydi.objects.order_by("id"))
    assert [k.eylem for k in kayitlar] == [Eylem.DAVET, Eylem.DAVET_KABUL, Eylem.ROL_ATAMA, Eylem.ROL_KALDIRMA]
    assert kayitlar[0].kullanici == baskan and kayitlar[0].nesne_id == str(davet.pk)
    assert kayitlar[1].kullanici == yeni
    assert kayitlar[2].kullanici == baskan and kayitlar[2].ayrinti["hedef_kullanici"] == yeni.pk
    assert kayitlar[3].nesne_turu == "accounts.rolatamasi" and kayitlar[3].ayrinti["rol"] == Rol.EDITOR
    for k in kayitlar:
        metin = str(k.ayrinti)
        assert "gizli" not in metin.lower() and "@" not in metin
