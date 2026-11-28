"""Ekip sayfası: onay akışı, yayın onayı ve API (PANEL.md §8, A3 kabul ölçütleri)."""

from datetime import date, timedelta

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Rol
from apps.ekip import servisler
from apps.ekip.models import Degisiklik, DegisiklikDurumu, Donem, GrupTuru, Kisi
from apps.onay import akis

from .conftest import resim

pytestmark = pytest.mark.django_db
API = reverse("api_ekip")
BUGUN = date(2026, 11, 1)


@pytest.fixture
def editor(kullanici_yap):
    return kullanici_yap(Rol.EDITOR, email="editor@ornek.org")


@pytest.fixture
def yk(kullanici_yap):
    return kullanici_yap(Rol.YONETIM_KURULU, "Başkan", email="yk@ornek.org")


@pytest.fixture
def donem(editor):
    return servisler.donem_olustur(editor, "2026–2027", date(2026, 10, 1), date(2027, 9, 30))


@pytest.fixture
def birim(editor, donem):
    return servisler.grup_kaydet(editor, donem, "İletişim Birimi", GrupTuru.BIRIM)


def kisi(editor, grup, ad="Ayşe Yılmaz", onay=BUGUN, **ek):
    veri = {"ad": ad, "gorev": "Üye", "eposta": "ornek@firat.edu.tr", "yayin_onayi_tarihi": onay, **ek}
    return servisler.kisi_kaydet(editor, grup, veri)


def yayimla(editor, yk, donem, ozet="Ekip güncellendi"):
    d = servisler.onaya_gonder(editor, donem, ozet)
    return akis.onayla(yk, d)


def test_yayin_onayi_olmayan_kisi_apide_gorunmez(client, editor, yk, donem, birim):
    kisi(editor, birim, "Onaylı Kişi")
    kisi(editor, birim, "Onaysız Kişi", onay=None)
    yayimla(editor, yk, donem)
    adlar = [k["ad"] for g in client.get(API).json()["gruplar"] for k in g["kisiler"]]
    assert adlar == ["Onaylı Kişi"]


def test_onaylanmadan_degisiklik_gorunmez(client, editor, yk, donem, birim):
    assert client.get(API).json() == {"donem": None, "yayin_tarihi": None, "gruplar": []}
    k = kisi(editor, birim)
    servisler.onaya_gonder(editor, donem, "İlk ekip")
    assert client.get(API).json()["gruplar"] == []  # onay bekliyor
    d = servisler.acik_degisiklik()
    akis.onayla(yk, d)
    assert client.get(API).json()["gruplar"][0]["kisiler"][0]["ad"] == "Ayşe Yılmaz"
    # Onaydan sonraki düzenleme yeniden onaylanana kadar sitede görünmez.
    servisler.kisi_kaydet(editor, birim, {"ad": "Değişmiş Ad"}, k)
    kisi(editor, birim, "Yeni Üye")
    assert [k["ad"] for k in client.get(API).json()["gruplar"][0]["kisiler"]] == ["Ayşe Yılmaz"]
    yayimla(editor, yk, donem, "İsim düzeltmesi")
    assert [k["ad"] for k in client.get(API).json()["gruplar"][0]["kisiler"]] == ["Değişmiş Ad", "Yeni Üye"]
    assert Degisiklik.objects.filter(durum=DegisiklikDurumu.YAYINDA).count() == 1
    assert Degisiklik.objects.filter(durum=DegisiklikDurumu.ESKI).count() == 1


def test_api_yalnizca_herkese_acik_alanlar(client, editor, yk, donem, birim, kullanici_yap):
    servisler.kisi_kaydet(
        editor,
        birim,
        {"ad": "A", "gorev": "Birim Sorumlusu", "eposta": "a@firat.edu.tr", "yayin_onayi_tarihi": BUGUN,
         "baglantilar": {"linkedin": "https://linkedin.com/in/ornek", "github": "https://github.com/ornek"}},
        foto=resim(),
    )
    Kisi.objects.update(kullanici=kullanici_yap())
    yayimla(editor, yk, donem)
    veri = client.get(API).json()
    assert set(veri) == {"donem", "yayin_tarihi", "gruplar"} and veri["donem"] == "2026–2027"
    k = veri["gruplar"][0]["kisiler"][0]
    assert set(k) == {"ad", "gorev", "birim", "eposta", "foto", "baglantilar"}
    assert k["foto"].startswith("http://testserver/medya/ekip/") and k["foto"].endswith(".jpg")
    assert k["baglantilar"] == [
        {"ad": "LinkedIn", "url": "https://linkedin.com/in/ornek"},
        {"ad": "GitHub", "url": "https://github.com/ornek"},
    ]
    assert "onay" not in str(veri["gruplar"]) and "kullanici" not in str(veri)


def test_api_yazma_istegi_reddedilir(client):
    assert client.post(API, data={}, content_type="application/json").status_code == 405


def test_editor_onaylayamaz_yk_onaylar(editor, yk, donem, birim):
    kisi(editor, birim)
    d = servisler.onaya_gonder(editor, donem, "x")
    with pytest.raises(PermissionDenied):
        akis.onayla(editor, d)
    akis.onayla(yk, d)
    d.refresh_from_db()
    assert d.durum == DegisiklikDurumu.YAYINDA and d.onaylayan == yk


@pytest.mark.parametrize("rol", [Rol.DANISMAN, Rol.TEKNIK, None])
def test_duzenleme_yetkisi_yok(kullanici_yap, donem, birim, rol):
    k = kullanici_yap(rol)
    with pytest.raises(PermissionDenied):
        servisler.grup_kaydet(k, donem, "x", GrupTuru.BIRIM)
    with pytest.raises(PermissionDenied):
        servisler.kisi_kaydet(k, birim, {"ad": "x", "gorev": "Üye"})
    with pytest.raises(PermissionDenied):
        servisler.onaya_gonder(k, donem, "x")
    with pytest.raises(PermissionDenied):
        servisler.donem_olustur(k, "2030", date(2030, 1, 1), date(2030, 12, 1))


def test_suresi_dolmus_editor_duzenleyemez(kullanici_yap, birim):
    dun = timezone.localdate() - timedelta(days=1)
    k = kullanici_yap(Rol.EDITOR, baslangic=dun - timedelta(days=100), bitis=dun)
    with pytest.raises(PermissionDenied):
        servisler.kisi_kaydet(k, birim, {"ad": "x", "gorev": "Üye"})


def test_tek_acik_degisiklik_ve_duzeltme_sonrasi_yeniden_gonderim(editor, yk, donem, birim):
    kisi(editor, birim, "Bir")
    d = servisler.onaya_gonder(editor, donem, "İlk")
    with pytest.raises(ValidationError, match="geri çekin"):
        servisler.onaya_gonder(editor, donem, "İkinci")
    akis.duzeltme_iste(yk, d, "Fotoğraf eksik.")
    kisi(editor, birim, "İki")
    d2 = servisler.onaya_gonder(editor, donem, "Fotoğraf eklendi")
    assert d2.pk == d.pk and d2.durum == DegisiklikDurumu.ONAY_BEKLIYOR
    assert [k["ad"] for k in d2.veri["gruplar"][0]["kisiler"]] == ["Bir", "İki"]
    assert Degisiklik.objects.count() == 1


def test_bos_ekip_onaya_gitmez(editor, donem):
    with pytest.raises(ValidationError, match="grup yok"):
        servisler.onaya_gonder(editor, donem, "x")


def test_baglanti_dogrulama(editor, birim):
    for hatali in ({"linkedin": "http://linkedin.com/x"}, {"facebook": "https://facebook.com/x"}, {"github": "javascript:alert(1)"}):
        with pytest.raises(ValidationError):
            servisler.kisi_kaydet(editor, birim, {"ad": "x", "gorev": "Üye", "baglantilar": hatali})
    assert not Kisi.objects.exists()


def test_foto_degisince_eski_dosya_yerinde_kalir(editor, yk, donem, birim, gecici_medya):
    k = servisler.kisi_kaydet(editor, birim, {"ad": "A", "gorev": "Üye", "yayin_onayi_tarihi": BUGUN}, foto=resim())
    eski = k.foto.name
    yayimla(editor, yk, donem)
    k = servisler.kisi_kaydet(editor, birim, {}, k, foto=resim(renk=(0, 0, 200)))
    assert k.foto.name != eski
    assert (gecici_medya / eski).exists()  # yayındaki sürüm hâlâ eski fotoğrafı gösteriyor
    k = servisler.kisi_kaydet(editor, birim, {}, k, foto_kaldir=True)
    assert k.foto.name == ""


def test_donem_kopyalama_ve_tek_aktif(editor, donem, birim):
    kisi(editor, birim)
    servisler.grup_kaydet(editor, donem, "Yönetim", GrupTuru.YONETIM)
    yeni = servisler.donem_olustur(editor, "2027–2028", date(2027, 10, 1), date(2028, 9, 30), kopyalanacak=donem)
    donem.refresh_from_db()
    assert yeni.aktif and not donem.aktif and Donem.objects.filter(aktif=True).count() == 1
    assert [g.ad for g in yeni.gruplar.all()] == ["İletişim Birimi", "Yönetim"]
    assert yeni.gruplar.first().kisiler.get().ad == "Ayşe Yılmaz"
    assert birim.kisiler.count() == 1  # eski dönem dokunulmadan kalır
    with pytest.raises(ValidationError):
        servisler.donem_olustur(editor, "2027–2028", date(2027, 10, 1), date(2028, 9, 30))


def test_siralama(editor, birim):
    a, b, c = (kisi(editor, birim, ad) for ad in "ABC")
    servisler.tasi(editor, c, -1)
    assert [k.ad for k in birim.kisiler.all()] == ["A", "C", "B"]
    servisler.tasi(editor, a, -1)  # en üstte: değişmez
    assert [k.ad for k in birim.kisiler.all()] == ["A", "C", "B"]
