"""Ekip ekranı: yetkisiz erişim, düzenleme, fotoğraf ve onay (PANEL.md §5, §8; A3)."""

import io
from datetime import date, timedelta

import pytest
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.accounts.models import Rol
from apps.ekip import servisler
from apps.ekip.models import Degisiklik, DegisiklikDurumu, Donem, Grup, GrupTuru, Kisi

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def gecici_medya(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def editor(kullanici_yap):
    return kullanici_yap(Rol.EDITOR, email="editor@ornek.org")


@pytest.fixture
def yk(kullanici_yap):
    return kullanici_yap(Rol.YONETIM_KURULU, "Başkan", email="yk@ornek.org")


@pytest.fixture
def donem(editor):
    return servisler.donem_olustur(editor, "2026–2027", date(2026, 10, 1), date(2027, 9, 30), varsayilan_gruplar=True)


@pytest.fixture
def grup(donem):
    return donem.gruplar.get(ad="İletişim Birimi")


@pytest.fixture
def kisi(editor, grup):
    return servisler.kisi_kaydet(editor, grup, {"ad": "Ayşe Yılmaz", "gorev": "Üye", "yayin_onayi_tarihi": date(2026, 11, 1)})


def foto(boyut=(900, 600)):
    t = io.BytesIO()
    exif = Image.Exif()
    exif[0x010F] = "Telefon"
    Image.new("RGB", boyut, (10, 120, 200)).save(t, format="JPEG", exif=exif)
    return SimpleUploadedFile("foto.jpg", t.getvalue(), content_type="image/jpeg")


def kisi_formu(**ek):
    return {"ad": "Deniz Kaya", "gorev": "Birim Sorumlusu", "eposta": "ornek@firat.edu.tr", **ek}


def adresler(grup, kisi, d=None):
    a = {
        "ana": ("get", reverse("panel:ekip")),
        "onizleme": ("get", reverse("panel:ekip_onizleme")),
        "donem": ("get", reverse("panel:ekip_donem_yeni")),
        "grup_yeni": ("get", reverse("panel:ekip_grup_yeni")),
        "grup": ("get", reverse("panel:ekip_grup", args=[grup.pk])),
        "grup_sil": ("get", reverse("panel:ekip_grup_sil", args=[grup.pk])),
        "kisi_yeni": ("get", reverse("panel:ekip_kisi_yeni", args=[grup.pk])),
        "kisi": ("get", reverse("panel:ekip_kisi", args=[kisi.pk])),
        "kisi_sil": ("get", reverse("panel:ekip_kisi_sil", args=[kisi.pk])),
        "tasi": ("post", reverse("panel:ekip_tasi", args=["kisi", kisi.pk])),
        "onaya": ("post", reverse("panel:ekip_onaya_gonder")),
    }
    if d is not None:
        a |= {
            "degisiklik": ("get", reverse("panel:ekip_degisiklik", args=[d.pk])),
            "onayla": ("post", reverse("panel:ekip_degisiklik_onayla", args=[d.pk])),
            "duzeltme": ("post", reverse("panel:ekip_degisiklik_duzeltme", args=[d.pk])),
            "geri": ("post", reverse("panel:ekip_degisiklik_geri_cek", args=[d.pk])),
        }
    return a


def iste(client, yontem, adres):
    return client.post(adres, {"ozet": "x", "not_": "x", "yon": "yukari", "ad": "x", "tur": "birim"}) if yontem == "post" else client.get(adres)


def test_giris_yapmamis_ve_dogrulanmamis(client, editor, grup, kisi):
    d = servisler.onaya_gonder(editor, grup.donem, "x")
    for ad, (y, adres) in adresler(grup, kisi, d).items():
        assert iste(client, y, adres)["Location"].startswith(reverse("panel:giris")), ad
    client.force_login(editor)
    for ad, (y, adres) in adresler(grup, kisi, d).items():
        assert iste(client, y, adres)["Location"] == reverse("panel:kurulum"), ad


@pytest.mark.parametrize("rol", [None, Rol.TEKNIK])
def test_rolsuz_ve_teknik_giremez(client, kullanici_yap, tam_giris, editor, grup, kisi, rol):
    d = servisler.onaya_gonder(editor, grup.donem, "x")
    tam_giris(kullanici_yap(rol))
    for ad, (y, adres) in adresler(grup, kisi, d).items():
        assert iste(client, y, adres).status_code == 403, ad
    d.refresh_from_db()
    assert d.durum == DegisiklikDurumu.ONAY_BEKLIYOR and Kisi.objects.count() == 1


def test_danisman_gorur_degistiremez(client, kullanici_yap, tam_giris, editor, grup, kisi):
    d = servisler.onaya_gonder(editor, grup.donem, "x")
    tam_giris(kullanici_yap(Rol.DANISMAN))
    a = adresler(grup, kisi, d)
    for ad in ("ana", "onizleme", "degisiklik"):
        assert client.get(a[ad][1]).status_code == 200, ad
    assert "Kişi ekle" not in client.get(a["ana"][1]).content.decode()
    for ad in ("donem", "grup_yeni", "grup", "kisi_yeni", "kisi", "kisi_sil", "tasi", "onaya", "onayla", "duzeltme", "geri"):
        assert iste(client, *a[ad]).status_code == 403, ad
    assert client.post(a["kisi"][1], kisi_formu()).status_code == 403
    kisi.refresh_from_db()
    assert kisi.ad == "Ayşe Yılmaz"


def test_suresi_dolmus_editor_giremez(client, kullanici_yap, tam_giris, grup):
    dun = timezone.localdate() - timedelta(days=1)
    tam_giris(kullanici_yap(Rol.EDITOR, baslangic=dun - timedelta(days=100), bitis=dun))
    assert client.get(reverse("panel:ekip")).status_code == 403
    assert client.post(reverse("panel:ekip_kisi_yeni", args=[grup.pk]), kisi_formu()).status_code == 403


def test_editor_onaylayamaz(client, tam_giris, editor, grup, kisi):
    d = servisler.onaya_gonder(editor, grup.donem, "x")
    tam_giris(editor)
    assert client.post(reverse("panel:ekip_degisiklik_onayla", args=[d.pk])).status_code == 403
    assert client.post(reverse("panel:ekip_degisiklik_duzeltme", args=[d.pk]), {"not_": "x"}).status_code == 403


def test_onaylar_yalnizca_post(client, tam_giris, yk, editor, grup, kisi):
    d = servisler.onaya_gonder(editor, grup.donem, "x")
    tam_giris(yk)
    for ad in ("ekip_degisiklik_onayla", "ekip_degisiklik_duzeltme", "ekip_degisiklik_geri_cek"):
        assert client.get(reverse(f"panel:{ad}", args=[d.pk])).status_code == 405
    assert client.get(reverse("panel:ekip_onaya_gonder")).status_code == 405


def test_eski_donemin_kisisi_url_ile_duzenlenemez(client, tam_giris, editor, grup, kisi):
    servisler.donem_olustur(editor, "2027–2028", date(2027, 10, 1), date(2028, 9, 30), kopyalanacak=grup.donem)
    tam_giris(editor)
    assert client.get(reverse("panel:ekip_kisi", args=[kisi.pk])).status_code == 404
    assert client.post(reverse("panel:ekip_kisi_sil", args=[kisi.pk])).status_code == 404
    assert client.post(reverse("panel:ekip_tasi", args=["baska", kisi.pk])).status_code == 404


def test_ilk_donem_varsayilan_gruplarla(client, tam_giris, editor):
    tam_giris(editor)
    assert "Henüz dönem yok" in client.get(reverse("panel:ekip")).content.decode()
    client.post(reverse("panel:ekip_donem_yeni"), {"ad": "2026–2027", "baslangic": "2026-10-01", "bitis": "2027-09-30", "baslangic_icerigi": "varsayilan"})
    d = Donem.objects.get()
    assert d.aktif and [g.ad for g in d.gruplar.all()][:2] == ["Akademik Danışman", "Yönetim"] and d.gruplar.count() == 6


def test_kisi_ekleme_foto_ve_yayin_onayi(client, tam_giris, editor, grup):
    tam_giris(editor)
    yanit = client.post(
        reverse("panel:ekip_kisi_yeni", args=[grup.pk]),
        kisi_formu(foto=foto(), yayin_onayi="on", baglanti_linkedin="https://linkedin.com/in/ornek"),
    )
    assert yanit["Location"] == reverse("panel:ekip")
    k = Kisi.objects.get()
    assert k.yayin_onayi_tarihi == timezone.localdate() and k.baglantilar == {"linkedin": "https://linkedin.com/in/ornek"}
    with Image.open(k.foto.path) as g:
        assert g.size == (800, 800) and len(g.getexif()) == 0
    # Onay kutusu kaldırılınca tarih silinir; yeniden işaretlenince bugünün tarihi.
    client.post(reverse("panel:ekip_kisi", args=[k.pk]), kisi_formu())
    k.refresh_from_db()
    assert k.yayin_onayi_tarihi is None and k.foto  # fotoğraf korunur


def test_hatali_foto_ve_baglanti_formda_gorunur(client, tam_giris, editor, grup):
    tam_giris(editor)
    sahte = SimpleUploadedFile("foto.jpg", b"<?php system($_GET['x']); ?>", content_type="image/jpeg")
    yanit = client.post(reverse("panel:ekip_kisi_yeni", args=[grup.pk]), kisi_formu(foto=sahte))
    assert yanit.status_code == 200 and "geçerli bir fotoğraf" in yanit.content.decode()
    yanit = client.post(reverse("panel:ekip_kisi_yeni", args=[grup.pk]), kisi_formu(baglanti_github="http://github.com/x"))
    assert yanit.status_code == 200 and "https://" in yanit.content.decode()
    assert not Kisi.objects.exists()


def test_tam_akis_ve_eposta(client, tam_giris, editor, yk, grup, kisi):
    servisler.kisi_kaydet(editor, grup, {"ad": "Onaysız", "gorev": "Üye"})
    tam_giris(editor)
    client.post(reverse("panel:ekip_onaya_gonder"), {"ozet": "İletişim Birimi güncellendi"})
    d = Degisiklik.objects.get()
    assert d.durum == DegisiklikDurumu.ONAY_BEKLIYOR
    assert mail.outbox[-1].to == ["yk@ornek.org"] and f"/ekip/degisiklik/{d.pk}/" in mail.outbox[-1].body
    tam_giris(yk)
    sayfa = client.get(reverse("panel:ekip_degisiklik", args=[d.pk])).content.decode()
    assert "Ayşe Yılmaz" in sayfa and "Onaysız" not in sayfa and "eklenen: Ayşe Yılmaz" in sayfa
    assert client.get(reverse("panel:ana")).context["ekip_bekleyen"] == d
    client.post(reverse("panel:ekip_degisiklik_onayla", args=[d.pk]))
    assert [k["ad"] for g in client.get(reverse("api_ekip")).json()["gruplar"] for k in g["kisiler"]] == ["Ayşe Yılmaz"]


def test_duzeltme_ve_geri_cekme(client, tam_giris, editor, yk, kullanici_yap, grup, kisi):
    tam_giris(editor)
    client.post(reverse("panel:ekip_onaya_gonder"), {"ozet": "x"})
    d = Degisiklik.objects.get()
    tam_giris(yk)
    client.post(reverse("panel:ekip_degisiklik_duzeltme", args=[d.pk]), {"not_": "Fotoğraf eksik."})
    d.refresh_from_db()
    assert d.durum == DegisiklikDurumu.TASLAK and mail.outbox[-1].to == ["editor@ornek.org"]
    tam_giris(editor)
    assert "Fotoğraf eksik." in client.get(reverse("panel:ekip_degisiklik", args=[d.pk])).content.decode()
    client.post(reverse("panel:ekip_onaya_gonder"), {"ozet": "Fotoğraf eklendi"})
    d.refresh_from_db()
    assert d.durum == DegisiklikDurumu.ONAY_BEKLIYOR
    tam_giris(kullanici_yap(Rol.EDITOR))
    assert client.post(reverse("panel:ekip_degisiklik_geri_cek", args=[d.pk])).status_code == 403
    tam_giris(editor)
    client.post(reverse("panel:ekip_degisiklik_geri_cek", args=[d.pk]))
    d.refresh_from_db()
    assert d.durum == DegisiklikDurumu.TASLAK


def test_siralama_ve_silme(client, tam_giris, editor, grup, kisi):
    ikinci = servisler.kisi_kaydet(editor, grup, {"ad": "İkinci", "gorev": "Üye"})
    tam_giris(editor)
    client.post(reverse("panel:ekip_tasi", args=["kisi", ikinci.pk]), {"yon": "yukari"})
    assert [k.ad for k in grup.kisiler.all()] == ["İkinci", "Ayşe Yılmaz"]
    assert client.get(reverse("panel:ekip_kisi_sil", args=[kisi.pk])).status_code == 200 and Kisi.objects.count() == 2
    client.post(reverse("panel:ekip_kisi_sil", args=[kisi.pk]))
    assert list(Kisi.objects.values_list("ad", flat=True)) == ["İkinci"]
    client.post(reverse("panel:ekip_grup_sil", args=[grup.pk]))
    assert not Grup.objects.filter(pk=grup.pk).exists()


def test_html_kacislanir(client, tam_giris, editor, yk, grup):
    servisler.kisi_kaydet(editor, grup, {"ad": "<script>x()</script>", "gorev": "<b>g</b>", "yayin_onayi_tarihi": date(2026, 1, 1)})
    tam_giris(editor)
    for adres in (reverse("panel:ekip"), reverse("panel:ekip_onizleme")):
        sayfa = client.get(adres).content.decode()
        assert "<script>x()</script>" not in sayfa and "<b>g</b>" not in sayfa
