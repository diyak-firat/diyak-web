"""Kullanıcılar ekranı: yetkisiz erişim ve işlemler (PANEL.md §4, §5, §9).

Her görünüm için: giriş yapmamış, 2FA doğrulanmamış, rolsüz, süresi dolmuş rol ve yanlış rol.
"""

from datetime import timedelta

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import GOREV_BASKAN_YARDIMCISI, Davet, Rol, RolAtamasi
from apps.denetim.models import Eylem, IslemKaydi

pytestmark = pytest.mark.django_db
BUGUN = timezone.localdate


@pytest.fixture
def hedef(kullanici_yap):
    return kullanici_yap(Rol.EDITOR, "İletişim Birimi", email="hedef@ornek.org", first_name="Hedef", last_name="Kişi")


def adresler(hedef):
    atama = RolAtamasi.objects.filter(kullanici=hedef).first()
    return [
        reverse("panel:kullanicilar"),
        reverse("panel:kullanici_davet"),
        reverse("panel:kullanici", args=[hedef.pk]),
        reverse("panel:kullanici_rol_kaldir", args=[hedef.pk, atama.pk]),
        reverse("panel:kullanici_kapat", args=[hedef.pk]),
        reverse("panel:kullanici_iki_adim_sifirla", args=[hedef.pk]),
    ]


def test_giris_yapmamis_kisi_giris_sayfasina_gider(client, hedef):
    for adres in adresler(hedef) + [reverse("panel:kullanici_kilidi_ac", args=[hedef.pk])]:
        yanit = client.get(adres) if "kilidi" not in adres else client.post(adres)
        assert yanit.status_code == 302 and yanit["Location"].startswith(reverse("panel:giris")), adres


def test_2fa_dogrulanmamis_baskan_giremez(client, baskan, hedef):
    TOTPDevice.objects.create(user=baskan, name="T", confirmed=True)
    client.force_login(baskan)
    for adres in adresler(hedef):
        assert client.get(adres)["Location"] == reverse("panel:iki_adim"), adres


@pytest.mark.parametrize(
    "rol,gorev",
    [(None, ""), (Rol.EDITOR, ""), (Rol.DANISMAN, ""), (Rol.YONETIM_KURULU, ""), (Rol.YONETIM_KURULU, "Sayman")],
)
def test_yetkisiz_roller_403(client, kullanici_yap, tam_giris, hedef, rol, gorev):
    tam_giris(kullanici_yap(rol, gorev))
    for adres in adresler(hedef):
        assert client.get(adres).status_code == 403, adres
        assert client.post(adres, {"rol": Rol.EDITOR, "bitis": "2099-01-01", "eposta": "x@ornek.org"}).status_code == 403
    assert client.post(reverse("panel:kullanici_kilidi_ac", args=[hedef.pk])).status_code == 403
    assert RolAtamasi.objects.filter(kullanici=hedef).count() == 1
    assert not Davet.objects.exists()


def test_suresi_dolmus_baskan_403(client, kullanici_yap, tam_giris, hedef):
    dun = BUGUN() - timedelta(days=1)
    tam_giris(kullanici_yap(Rol.YONETIM_KURULU, "Başkan", baslangic=dun - timedelta(days=300), bitis=dun))
    for adres in adresler(hedef):
        assert client.get(adres).status_code == 403, adres


def test_menude_kullanicilar_yalnizca_yetkiliye_gorunur(client, kullanici_yap, tam_giris, baskan):
    tam_giris(kullanici_yap(Rol.EDITOR))
    assert reverse("panel:kullanicilar") not in client.get(reverse("panel:ana")).content.decode()
    tam_giris(baskan)
    assert reverse("panel:kullanicilar") in client.get(reverse("panel:ana")).content.decode()


def test_baskan_listeyi_gorur(client, tam_giris, baskan, hedef):
    tam_giris(baskan)
    icerik = client.get(reverse("panel:kullanicilar")).content.decode()
    assert "hedef@ornek.org" in icerik and "İletişim Birimi" in icerik


def test_yakinda_bitecek_roller_listelenir(client, tam_giris, baskan, kullanici_yap):
    kullanici_yap(Rol.EDITOR, email="bitiyor@ornek.org", bitis=BUGUN() + timedelta(days=10))
    kullanici_yap(Rol.EDITOR, email="uzun@ornek.org", bitis=BUGUN() + timedelta(days=60))
    tam_giris(baskan)
    yanit = client.get(reverse("panel:kullanicilar"))
    bitecekler = [a.kullanici.email for a in yanit.context["yakinda_bitenler"]]
    assert bitecekler == ["bitiyor@ornek.org"]


def test_baskan_davet_gonderir(client, tam_giris, baskan, donem_sonu):
    tam_giris(baskan)
    yanit = client.post(
        reverse("panel:kullanici_davet"),
        {"eposta": "Yeni@Ornek.org", "rol": Rol.EDITOR, "gorev_adi": "Medya Birimi", "bitis": donem_sonu.isoformat()},
    )
    assert yanit["Location"] == reverse("panel:kullanicilar")
    davet = Davet.objects.get()
    assert (davet.eposta, davet.rol, davet.davet_eden) == ("yeni@ornek.org", Rol.EDITOR, baskan)
    assert len(mail.outbox) == 1 and mail.outbox[0].to == ["yeni@ornek.org"]
    assert "/davet/" in mail.outbox[0].body
    assert "yeni@ornek.org" in client.get(reverse("panel:kullanicilar")).content.decode()


def test_davet_formunda_teknik_rolu_baskana_sunulmaz(client, tam_giris, baskan, donem_sonu):
    tam_giris(baskan)
    form = client.get(reverse("panel:kullanici_davet")).context["form"]
    assert [c for c, _ in form.fields["rol"].choices] == ["", Rol.YONETIM_KURULU, Rol.EDITOR, Rol.DANISMAN]
    assert form.initial["bitis"] == RolAtamasi.objects.get(kullanici=baskan).bitis
    yanit = client.post(reverse("panel:kullanici_davet"), {"eposta": "t@ornek.org", "rol": Rol.TEKNIK, "bitis": donem_sonu.isoformat()})
    assert yanit.status_code == 200 and not Davet.objects.exists()


def test_var_olan_hesaba_davet_hatasi_formda_gorunur(client, tam_giris, baskan, hedef, donem_sonu):
    tam_giris(baskan)
    yanit = client.post(reverse("panel:kullanici_davet"), {"eposta": "hedef@ornek.org", "rol": Rol.EDITOR, "bitis": donem_sonu.isoformat()})
    assert yanit.status_code == 200 and "zaten var" in yanit.content.decode()


def test_teknik_yalnizca_teknik_davet_eder(client, tam_giris, teknik, donem_sonu):
    tam_giris(teknik)
    form = client.get(reverse("panel:kullanici_davet")).context["form"]
    assert [c for c, _ in form.fields["rol"].choices] == [Rol.TEKNIK]
    client.post(reverse("panel:kullanici_davet"), {"eposta": "e@ornek.org", "rol": Rol.EDITOR, "bitis": donem_sonu.isoformat()})
    assert not Davet.objects.exists()


def test_baskan_rol_atar_ve_kaldirir(client, tam_giris, baskan, hedef, donem_sonu):
    tam_giris(baskan)
    adres = reverse("panel:kullanici", args=[hedef.pk])
    yanit = client.post(adres, {"rol": Rol.DANISMAN, "gorev_adi": "", "bitis": donem_sonu.isoformat()})
    assert yanit["Location"] == adres
    atama = RolAtamasi.objects.get(kullanici=hedef, rol=Rol.DANISMAN)

    kaldir = reverse("panel:kullanici_rol_kaldir", args=[hedef.pk, atama.pk])
    onay = client.get(kaldir)
    assert onay.status_code == 200 and "Danışman" in onay.content.decode()
    assert RolAtamasi.objects.filter(pk=atama.pk).exists()  # GET yalnızca onay sorar
    client.post(kaldir)
    assert not RolAtamasi.objects.filter(pk=atama.pk).exists()
    assert IslemKaydi.objects.filter(eylem=Eylem.ROL_KALDIRMA, kullanici=baskan).exists()


def test_baskan_teknik_rolunu_kaldiramaz(client, tam_giris, baskan, teknik):
    tam_giris(baskan)
    atama = RolAtamasi.objects.get(kullanici=teknik)
    adres = reverse("panel:kullanici_rol_kaldir", args=[teknik.pk, atama.pk])
    assert client.get(adres).status_code == 403
    assert client.post(adres).status_code == 403
    assert RolAtamasi.objects.filter(pk=atama.pk).exists()


def test_teknik_editor_rolunu_kaldiramaz(client, tam_giris, teknik, hedef):
    tam_giris(teknik)
    atama = RolAtamasi.objects.get(kullanici=hedef)
    assert client.post(reverse("panel:kullanici_rol_kaldir", args=[hedef.pk, atama.pk])).status_code == 403


def test_baska_kisinin_atamasi_url_ile_kaldirilamaz(client, tam_giris, baskan, hedef, kullanici_yap):
    tam_giris(baskan)
    baska = kullanici_yap(Rol.EDITOR)
    atama = RolAtamasi.objects.get(kullanici=baska)
    assert client.post(reverse("panel:kullanici_rol_kaldir", args=[hedef.pk, atama.pk])).status_code == 404
    assert RolAtamasi.objects.filter(pk=atama.pk).exists()


def test_baskan_yardimcisi_hesap_kapatir(client, tam_giris, kullanici_yap, hedef):
    tam_giris(kullanici_yap(Rol.YONETIM_KURULU, GOREV_BASKAN_YARDIMCISI))
    adres = reverse("panel:kullanici_kapat", args=[hedef.pk])
    assert client.get(adres).status_code == 200
    client.post(adres)
    hedef.refresh_from_db()
    assert not hedef.is_active
    assert IslemKaydi.objects.filter(eylem=Eylem.HESAP_KAPATMA, nesne_id=str(hedef.pk)).exists()


def test_kendi_hesabini_ve_teknigi_kapatamaz(client, tam_giris, baskan, teknik):
    tam_giris(baskan)
    assert client.post(reverse("panel:kullanici_kapat", args=[baskan.pk])).status_code == 403
    assert client.post(reverse("panel:kullanici_kapat", args=[teknik.pk])).status_code == 403
    teknik.refresh_from_db()
    assert teknik.is_active


def test_kapatilan_hesabin_oturumu_duser(client, tam_giris, baskan, hedef):
    from django.test import Client

    from conftest import dogrulanmis_giris

    hedef_istemci = Client()
    dogrulanmis_giris(hedef_istemci, hedef)
    assert hedef_istemci.get(reverse("panel:ana")).status_code == 200
    tam_giris(baskan)
    client.post(reverse("panel:kullanici_kapat", args=[hedef.pk]))
    assert hedef_istemci.get(reverse("panel:ana")).status_code == 302


def test_teknik_2fa_sifirlar_baskan_sifirlayamaz(client, tam_giris, teknik, baskan, hedef):
    TOTPDevice.objects.create(user=hedef, name="Telefon", confirmed=True)
    adres = reverse("panel:kullanici_iki_adim_sifirla", args=[hedef.pk])
    tam_giris(baskan)
    assert client.post(adres).status_code == 403
    assert TOTPDevice.objects.filter(user=hedef).exists()
    tam_giris(teknik)
    assert client.get(adres).status_code == 200
    client.post(adres)
    assert not TOTPDevice.objects.filter(user=hedef).exists()
    kayit = IslemKaydi.objects.get(eylem=Eylem.IKI_ADIM_SIFIRLAMA)
    assert kayit.kullanici == teknik and kayit.ayrinti == {"silinen_cihaz": 1}


def test_teknik_kendi_2fasini_sifirlayamaz(client, tam_giris, teknik):
    tam_giris(teknik)
    assert client.post(reverse("panel:kullanici_iki_adim_sifirla", args=[teknik.pk])).status_code == 403


def test_teknik_kilidi_acar(client, tam_giris, teknik, hedef):
    from axes.models import AccessAttempt

    for _ in range(5):
        client.post(reverse("panel:giris"), {"username": "hedef@ornek.org", "password": "yanlis-sifre-000"})
    assert AccessAttempt.objects.filter(username="hedef@ornek.org").exists()
    tam_giris(teknik)
    detay = client.get(reverse("panel:kullanici", args=[hedef.pk]))
    assert detay.context["kilitli"]
    assert client.get(reverse("panel:kullanici_kilidi_ac", args=[hedef.pk])).status_code == 405
    client.post(reverse("panel:kullanici_kilidi_ac", args=[hedef.pk]))
    assert not AccessAttempt.objects.filter(username="hedef@ornek.org").exists()
    assert IslemKaydi.objects.filter(eylem=Eylem.KILIT_ACMA, kullanici=teknik).exists()


def test_olmayan_kullanici_404(client, tam_giris, baskan):
    tam_giris(baskan)
    assert client.get(reverse("panel:kullanici", args=[999999])).status_code == 404


def test_html_kacislanir(client, tam_giris, baskan, kullanici_yap):
    kullanici_yap(Rol.EDITOR, "<script>alert(1)</script>", first_name="<b>x</b>")
    tam_giris(baskan)
    icerik = client.get(reverse("panel:kullanicilar")).content.decode()
    assert "<script>alert(1)</script>" not in icerik and "&lt;script&gt;" in icerik


def test_baskan_kendi_sayfasinda_rol_atayamaz(client, tam_giris, baskan, donem_sonu):
    tam_giris(baskan)
    adres = reverse("panel:kullanici", args=[baskan.pk])
    sayfa = client.get(adres)
    assert sayfa.status_code == 200
    assert sayfa.context["form"] is None and sayfa.context["kendisi"]
    assert not any(s["kaldirabilir"] for s in sayfa.context["atamalar"])
    assert "Kendi rollerinizi değiştiremezsiniz" in sayfa.content.decode()
    yanit = client.post(adres, {"rol": Rol.DANISMAN, "gorev_adi": "", "bitis": donem_sonu.isoformat()})
    assert yanit.status_code == 403
    assert list(RolAtamasi.objects.filter(kullanici=baskan).values_list("rol", flat=True)) == [Rol.YONETIM_KURULU]


def test_baskan_kendi_rolunu_url_ile_kaldiramaz(client, tam_giris, baskan):
    tam_giris(baskan)
    atama = RolAtamasi.objects.get(kullanici=baskan)
    adres = reverse("panel:kullanici_rol_kaldir", args=[baskan.pk, atama.pk])
    assert client.get(adres).status_code == 403
    assert client.post(adres).status_code == 403
    assert RolAtamasi.objects.filter(pk=atama.pk).exists()


def test_teknik_kendi_sayfasinda_rol_atayamaz(client, tam_giris, teknik, donem_sonu):
    tam_giris(teknik)
    adres = reverse("panel:kullanici", args=[teknik.pk])
    assert client.post(adres, {"rol": Rol.TEKNIK, "bitis": donem_sonu.isoformat()}).status_code == 403
    assert RolAtamasi.objects.filter(kullanici=teknik).count() == 1
