from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Rol
from apps.duyurular.models import Duyuru
from apps.etkinlikler import servisler
from apps.etkinlikler.models import Etkinlik

pytestmark = pytest.mark.django_db
GELECEK = (timezone.localtime() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M")


@pytest.fixture
def editor(kullanici_yap):
    return kullanici_yap(Rol.EDITOR)


@pytest.fixture
def etkinlik(editor):
    return servisler.kaydet_etkinlik(editor, {"ad": "Atölye", "baslangic": timezone.now() + timedelta(days=3), "yer": "[Salon]"})


def form(**ek):
    return {"ad": "Okuma grubu", "baslangic": GELECEK, "yer": "[Salon]", **ek}


def adresler(e):
    return [reverse("panel:etkinlikler"), reverse("panel:etkinlik_yeni"), reverse("panel:etkinlik", args=[e.pk]), reverse("panel:etkinlik_sil", args=[e.pk])]


def test_giris_ve_2fa(client, editor, etkinlik):
    for a in adresler(etkinlik):
        assert client.get(a)["Location"].startswith(reverse("panel:giris"))
    client.force_login(editor)
    for a in adresler(etkinlik):
        assert client.get(a)["Location"] == reverse("panel:kurulum")


@pytest.mark.parametrize("rol", [None, Rol.TEKNIK])
def test_rolsuz_ve_teknik(client, kullanici_yap, tam_giris, etkinlik, rol):
    tam_giris(kullanici_yap(rol))
    for a in adresler(etkinlik):
        assert client.get(a).status_code == 403
        assert client.post(a, form()).status_code == 403
    assert Etkinlik.objects.count() == 1


def test_suresi_dolmus_editor(client, kullanici_yap, tam_giris, etkinlik):
    dun = timezone.localdate() - timedelta(days=1)
    tam_giris(kullanici_yap(Rol.EDITOR, baslangic=dun - timedelta(days=50), bitis=dun))
    assert client.get(reverse("panel:etkinlikler")).status_code == 403


def test_danisman_gorur_degistiremez(client, kullanici_yap, tam_giris, etkinlik):
    tam_giris(kullanici_yap(Rol.DANISMAN))
    assert client.get(reverse("panel:etkinlikler")).status_code == 200
    sayfa = client.get(reverse("panel:etkinlik", args=[etkinlik.pk]))
    assert sayfa.status_code == 200 and sayfa.context["form"] is None
    assert client.post(reverse("panel:etkinlik", args=[etkinlik.pk]), form(ad="x")).status_code == 403
    assert client.get(reverse("panel:etkinlik_yeni")).status_code == 403


def test_olustur_harita_ve_hata(client, tam_giris, editor):
    tam_giris(editor)
    yanit = client.post(reverse("panel:etkinlik_yeni"), form(harita_baglantisi="https://kotu.example/maps"))
    assert yanit.status_code == 200 and "Paylaş" in yanit.content.decode() and not Etkinlik.objects.exists()
    yanit = client.post(reverse("panel:etkinlik_yeni"), form(harita_baglantisi="https://maps.app.goo.gl/AbC"))
    e = Etkinlik.objects.get()
    assert yanit["Location"] == reverse("panel:etkinlik", args=[e.pk])
    sayfa = client.get(reverse("panel:etkinlikler")).content.decode()
    assert 'href="https://maps.app.goo.gl/AbC"' in sayfa and 'rel="noopener noreferrer"' in sayfa


def test_duyuruda_var_olan_etkinligi_secme(client, tam_giris, editor, etkinlik):
    tam_giris(editor)
    client.post(
        reverse("panel:duyuru_yeni"),
        {"baslik": "Atölye duyurusu", "etiket": "etkinlik", "ozet": "ö", "govde": "<p>x</p>", "etkinlik_secimi": str(etkinlik.pk)},
    )
    d = Duyuru.objects.get()
    assert d.etkinlik == etkinlik and Etkinlik.objects.count() == 1  # ikinci etkinlik açılmadı
    sayfa = client.get(reverse("panel:etkinlik", args=[etkinlik.pk])).content.decode()
    assert "Atölye duyurusu" in sayfa


def test_duyuruda_yeni_etkinlik_harita_ile(client, tam_giris, editor):
    tam_giris(editor)
    client.post(
        reverse("panel:duyuru_yeni"),
        {"baslik": "Söyleşi", "etiket": "etkinlik", "ozet": "ö", "govde": "<p>x</p>", "etkinlik_secimi": "",
         "etkinlik_baslangic": GELECEK, "etkinlik_yer": "[Salon]", "etkinlik_harita": "https://maps.app.goo.gl/X"},
    )
    d = Duyuru.objects.get()
    assert d.etkinlik.harita_baglantisi == "https://maps.app.goo.gl/X"
    yanit = client.post(
        reverse("panel:duyuru_yeni"),
        {"baslik": "B", "etiket": "etkinlik", "ozet": "ö", "govde": "<p>x</p>", "etkinlik_secimi": "",
         "etkinlik_baslangic": GELECEK, "etkinlik_yer": "[Salon]", "etkinlik_harita": "https://kotu.example/x"},
    )
    assert yanit.status_code == 200 and Duyuru.objects.count() == 1


def test_olmayan_etkinlik_secilemez(client, tam_giris, editor):
    tam_giris(editor)
    yanit = client.post(
        reverse("panel:duyuru_yeni"),
        {"baslik": "A", "etiket": "etkinlik", "ozet": "ö", "govde": "<p>x</p>", "etkinlik_secimi": "99999"},
    )
    assert yanit.status_code == 200 and not Duyuru.objects.exists()  # seçenek listesinde yok: form hatası


def test_silme_onay_adimi(client, tam_giris, editor, etkinlik):
    tam_giris(editor)
    assert client.get(reverse("panel:etkinlik_sil", args=[etkinlik.pk])).status_code == 200
    client.post(reverse("panel:etkinlik_sil", args=[etkinlik.pk]))
    assert not Etkinlik.objects.exists()
