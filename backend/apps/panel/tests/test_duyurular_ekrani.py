"""Duyurular ekranları: yetkisiz erişim, onay akışı ve e-postalar (PANEL.md §5, §8, §9)."""

from datetime import timedelta

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Rol
from apps.denetim.models import Eylem, IslemKaydi
from apps.duyurular import servisler
from apps.duyurular.models import Durum, Duyuru, Etiket
from apps.onay import akis

pytestmark = pytest.mark.django_db
VERI = {"baslik": "Okuma grubu", "etiket": Etiket.DUYURU, "ozet": "Kısa özet.", "govde": "<p>Metin</p>"}


@pytest.fixture
def editor(kullanici_yap):
    return kullanici_yap(Rol.EDITOR, email="editor@ornek.org")


@pytest.fixture
def yk(kullanici_yap):
    return kullanici_yap(Rol.YONETIM_KURULU, "Sayman", email="yk@ornek.org")


@pytest.fixture
def taslak(editor):
    return servisler.kaydet_duyuru(editor, VERI)


@pytest.fixture
def bekleyen(editor, taslak):
    return akis.onaya_gonder(editor, taslak)


def form(**ek):
    return {"baslik": "Okuma grubu", "etiket": "duyuru", "ozet": "Kısa özet.", "govde": "<p>Metin</p>", **ek}


def adresler(d):
    return {
        "liste": reverse("panel:duyurular"),
        "yeni": reverse("panel:duyuru_yeni"),
        "detay": reverse("panel:duyuru", args=[d.pk]),
        "onizleme": reverse("panel:duyuru_onizleme", args=[d.pk]),
        "onaya_gonder": reverse("panel:duyuru_onaya_gonder", args=[d.pk]),
        "onayla": reverse("panel:duyuru_onayla", args=[d.pk]),
        "duzeltme": reverse("panel:duyuru_duzeltme_iste", args=[d.pk]),
        "geri_cek": reverse("panel:duyuru_geri_cek", args=[d.pk]),
        "sil": reverse("panel:duyuru_sil", args=[d.pk]),
    }


# ---------- Yetkisiz erişim ----------


YALNIZCA_POST = {"onaya_gonder", "onayla", "duzeltme", "geri_cek"}


def istek(client, ad, adres):
    return client.post(adres, {"not_": "x"}) if ad in YALNIZCA_POST else client.get(adres)


def test_giris_yapmamis_ve_dogrulanmamis(client, taslak, editor):
    for ad, adres in adresler(taslak).items():
        assert istek(client, ad, adres)["Location"].startswith(reverse("panel:giris")), ad
    client.force_login(editor)
    for ad, adres in adresler(taslak).items():
        assert istek(client, ad, adres)["Location"] == reverse("panel:kurulum"), ad
    taslak.refresh_from_db()
    assert taslak.durum == Durum.TASLAK


@pytest.mark.parametrize("rol", [None, Rol.TEKNIK])
def test_rolsuz_ve_teknik_hicbir_ekrani_acamaz(client, kullanici_yap, tam_giris, taslak, rol):
    tam_giris(kullanici_yap(rol))
    for ad, adres in adresler(taslak).items():
        assert client.get(adres).status_code in (403, 405), ad
        assert client.post(adres, form()).status_code == 403, ad
    assert Duyuru.objects.count() == 1 and Duyuru.objects.get().durum == Durum.TASLAK
    assert reverse("panel:duyurular") not in client.get(reverse("panel:hesabim")).content.decode()


def test_suresi_dolmus_editor_giremez(client, kullanici_yap, tam_giris, taslak):
    dun = timezone.localdate() - timedelta(days=1)
    tam_giris(kullanici_yap(Rol.EDITOR, baslangic=dun - timedelta(days=100), bitis=dun))
    assert client.get(reverse("panel:duyurular")).status_code == 403
    assert client.post(reverse("panel:duyuru", args=[taslak.pk]), form(baslik="x")).status_code == 403


def test_danisman_gorur_ama_degistiremez(client, kullanici_yap, tam_giris, bekleyen):
    tam_giris(kullanici_yap(Rol.DANISMAN))
    a = adresler(bekleyen)
    assert client.get(a["liste"]).status_code == 200
    sayfa = client.get(a["detay"])
    assert sayfa.status_code == 200 and "Onayla ve yayımla" not in sayfa.content.decode()
    assert client.get(a["yeni"]).status_code == 403
    for ad in ("detay", "onayla", "duzeltme", "onaya_gonder", "geri_cek"):
        assert client.post(a[ad], {**form(), "not_": "x"}).status_code == 403, ad
    bekleyen.refresh_from_db()
    assert bekleyen.durum == Durum.ONAY_BEKLIYOR


def test_editor_onaylayamaz_ve_yayimlayamaz(client, tam_giris, editor, bekleyen):
    tam_giris(editor)
    a = adresler(bekleyen)
    assert client.post(a["onayla"]).status_code == 403
    assert client.post(a["duzeltme"], {"not_": "x"}).status_code == 403
    assert "Onayla ve yayımla" not in client.get(a["detay"]).content.decode()
    yeni = client.post(reverse("panel:duyuru_yeni"), {**form(baslik="Gizli yayın"), "islem": "yayimla"})
    assert yeni.status_code == 403
    assert not Duyuru.objects.filter(baslik="Gizli yayın").exists()
    bekleyen.refresh_from_db()
    assert bekleyen.durum == Durum.ONAY_BEKLIYOR


def test_onaylar_yalnizca_post(client, tam_giris, yk, bekleyen):
    tam_giris(yk)
    a = adresler(bekleyen)
    for ad in ("onayla", "duzeltme", "onaya_gonder", "geri_cek"):
        assert client.get(a[ad]).status_code == 405, ad
    bekleyen.refresh_from_db()
    assert bekleyen.durum == Durum.ONAY_BEKLIYOR


def test_olmayan_duyuru_404(client, tam_giris, yk):
    tam_giris(yk)
    assert client.get(reverse("panel:duyuru", args=[99999])).status_code == 404
    assert client.post(reverse("panel:duyuru_onayla", args=[99999])).status_code == 404


# ---------- Akış ----------


def test_editor_yazar_onaya_gonderir_yk_eposta_alir(client, tam_giris, editor, yk, kullanici_yap):
    kullanici_yap(Rol.YONETIM_KURULU, "Başkan", email="baskan@ornek.org")
    tam_giris(editor)
    yanit = client.post(reverse("panel:duyuru_yeni"), {**form(), "islem": "onaya_gonder"})
    d = Duyuru.objects.get()
    assert yanit["Location"] == reverse("panel:duyuru", args=[d.pk])
    assert d.durum == Durum.ONAY_BEKLIYOR and d.olusturan == editor
    assert len(mail.outbox) == 1
    e = mail.outbox[0]
    assert sorted(e.to) == ["baskan@ornek.org", "yk@ornek.org"]
    assert "Okuma grubu" in e.body and f"/duyurular/{d.pk}/" in e.body and "Metin" not in e.body
    assert "onay vermez" in e.body
    # Onay bekleyen düzenlenemez: düzenleme POST'u reddedilir.
    assert client.post(reverse("panel:duyuru", args=[d.pk]), form(baslik="x")).status_code == 403


def test_yk_onay_ekraninda_onaylar(client, tam_giris, yk, bekleyen):
    tam_giris(yk)
    a = adresler(bekleyen)
    sayfa = client.get(a["detay"]).content.decode()
    assert "Onayla ve yayımla" in sayfa and "<p>Metin</p>" in sayfa
    client.post(a["onayla"])
    bekleyen.refresh_from_db()
    assert bekleyen.durum == Durum.YAYINDA and bekleyen.onaylayan == yk


def test_yk_duzeltme_ister_hazirlayan_eposta_alir(client, tam_giris, yk, editor, bekleyen):
    tam_giris(yk)
    a = adresler(bekleyen)
    client.post(a["duzeltme"], {"not_": ""})
    bekleyen.refresh_from_db()
    assert bekleyen.durum == Durum.ONAY_BEKLIYOR
    client.post(a["duzeltme"], {"not_": "Tarih eksik."})
    bekleyen.refresh_from_db()
    assert bekleyen.durum == Durum.TASLAK and bekleyen.onay_notu == "Tarih eksik."
    assert mail.outbox[-1].to == ["editor@ornek.org"] and "Tarih eksik" not in mail.outbox[-1].body
    tam_giris(editor)
    sayfa = client.get(a["detay"]).content.decode()
    assert "Tarih eksik." in sayfa and "Yönetim Kurulu düzeltme istedi" in sayfa


def test_yk_dogrudan_yayimlar_ve_kayitta_kendi_icerigi(client, tam_giris, yk):
    tam_giris(yk)
    client.post(reverse("panel:duyuru_yeni"), {**form(), "islem": "yayimla"})
    d = Duyuru.objects.get()
    assert d.durum == Durum.YAYINDA
    assert IslemKaydi.objects.get(eylem=Eylem.ONAYLAMA).ayrinti == {"kendi_icerigi": True}
    assert mail.outbox == []


def test_eksik_duyuru_onaya_gitmez_ama_taslak_kalir(client, tam_giris, editor):
    tam_giris(editor)
    yanit = client.post(reverse("panel:duyuru_yeni"), {**form(govde=""), "islem": "onaya_gonder"}, follow=True)
    assert "Metin boş" in yanit.content.decode()
    assert Duyuru.objects.get().durum == Durum.TASLAK


def test_etkinlik_alanlari(client, tam_giris, editor):
    tam_giris(editor)
    yanit = client.post(reverse("panel:duyuru_yeni"), form(etiket="etkinlik", etkinlik_yer="[Salon]"))
    assert yanit.status_code == 200 and not Duyuru.objects.exists()
    client.post(
        reverse("panel:duyuru_yeni"),
        {**form(etiket="etkinlik", etkinlik_baslangic="2027-03-14T15:00", etkinlik_yer="[Salon]"), "islem": "onaya_gonder"},
    )
    d = Duyuru.objects.get()
    assert d.durum == Durum.ONAY_BEKLIYOR and d.etkinlik.yer == "[Salon]"
    assert timezone.localtime(d.etkinlik.baslangic).strftime("%Y-%m-%d %H:%M") == "2027-03-14 15:00"


def test_govdedeki_script_temizlenir_ve_onizlemede_calismaz(client, tam_giris, editor):
    tam_giris(editor)
    client.post(reverse("panel:duyuru_yeni"), form(govde='<p>a</p><script>alert(1)</script><img src=x onerror="alert(2)">'))
    d = Duyuru.objects.get()
    assert d.govde == "<p>a</p>"
    sayfa = client.get(reverse("panel:duyuru_onizleme", args=[d.pk])).content.decode()
    assert "alert(" not in sayfa


def test_baslik_ve_ozet_kacislanir(client, tam_giris, editor):
    tam_giris(editor)
    client.post(reverse("panel:duyuru_yeni"), form(baslik="<b>x</b>", ozet="<script>y</script>"))
    d = Duyuru.objects.get()
    for adres in (reverse("panel:duyurular"), reverse("panel:duyuru", args=[d.pk]), reverse("panel:duyuru_onizleme", args=[d.pk])):
        sayfa = client.get(adres).content.decode()
        assert "<b>x</b>" not in sayfa and "<script>y</script>" not in sayfa, adres


def test_hazirlayan_geri_ceker_baska_editor_cekemez(client, tam_giris, editor, kullanici_yap, bekleyen):
    tam_giris(kullanici_yap(Rol.EDITOR))
    assert client.post(reverse("panel:duyuru_geri_cek", args=[bekleyen.pk])).status_code == 403
    tam_giris(editor)
    client.post(reverse("panel:duyuru_geri_cek", args=[bekleyen.pk]))
    bekleyen.refresh_from_db()
    assert bekleyen.durum == Durum.TASLAK


def test_yayindan_kaldirma_onay_adimi(client, tam_giris, yk, editor, bekleyen):
    akis.onayla(yk, bekleyen)
    adres = reverse("panel:duyuru_yayindan_kaldir", args=[bekleyen.pk])
    tam_giris(editor)
    assert client.post(adres).status_code == 403
    tam_giris(yk)
    assert client.get(adres).status_code == 200
    bekleyen.refresh_from_db()
    assert bekleyen.durum == Durum.YAYINDA
    client.post(adres)
    bekleyen.refresh_from_db()
    assert bekleyen.durum == Durum.KALDIRILDI


def test_taslak_silme_onay_adimi(client, tam_giris, editor, kullanici_yap, taslak):
    adres = reverse("panel:duyuru_sil", args=[taslak.pk])
    tam_giris(kullanici_yap(Rol.EDITOR))
    assert client.post(adres).status_code == 403
    tam_giris(editor)
    assert client.get(adres).status_code == 200 and Duyuru.objects.exists()
    client.post(adres)
    assert not Duyuru.objects.exists()


def test_ana_ekranda_onay_bekleyenler_ve_taslaklar(client, tam_giris, yk, editor, bekleyen):
    tam_giris(yk)
    yanit = client.get(reverse("panel:ana"))
    assert list(yanit.context["onay_bekleyenler"]) == [bekleyen]
    tam_giris(editor)
    yanit = client.get(reverse("panel:ana"))
    assert yanit.context["onay_bekleyenler"] is None and list(yanit.context["taslaklarim"]) == [bekleyen]


def test_filtreler(client, tam_giris, yk, editor, taslak):
    servisler.kaydet_duyuru(editor, {**VERI, "baslik": "Çağrı", "etiket": Etiket.CAGRI})
    tam_giris(yk)
    a = reverse("panel:duyurular")
    assert [d.etiket for d in client.get(a, {"etiket": "cagri"}).context["duyurular"]] == ["cagri"]
    assert client.get(a, {"durum": "yayinda"}).context["duyurular"].count() == 0
    assert client.get(a, {"durum": "<x>", "etiket": "?"}).status_code == 200
