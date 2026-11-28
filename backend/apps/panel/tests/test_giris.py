"""Giriş, 2FA, kilit ve yeni cihaz uyarısı (PANEL.md §9, §12 A1 kabul ölçütleri)."""

from datetime import timedelta

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import Rol
from apps.denetim.models import Eylem, IslemKaydi
from conftest import SIFRE

from .yardimci import guncel_kod

pytestmark = pytest.mark.django_db
GIRIS = reverse("panel:giris")
ANA = reverse("panel:ana")
IKI_ADIM = reverse("panel:iki_adim")
KURULUM = reverse("panel:kurulum")


def sifreyle_gir(client, eposta, sifre=SIFRE, **ek):
    return client.post(GIRIS, {"username": eposta, "password": sifre}, **ek)


@pytest.fixture
def editor(kullanici_yap):
    k = kullanici_yap(Rol.EDITOR, email="editor@ornek.org")
    TOTPDevice.objects.create(user=k, name="Telefon", confirmed=True)
    return k


def cihazi(k):
    return TOTPDevice.objects.get(user=k, confirmed=True)


def test_giris_yapmamis_kisi_giris_sayfasina_gider(client):
    yanit = client.get(ANA)
    assert yanit.status_code == 302 and yanit["Location"].startswith(GIRIS)


def test_sifre_dogru_ama_2fa_yoksa_panel_acilmaz(client, editor):
    yanit = sifreyle_gir(client, "editor@ornek.org")
    assert yanit["Location"] == IKI_ADIM
    yanit = client.get(ANA)
    assert yanit.status_code == 302 and yanit["Location"] == IKI_ADIM
    assert not IslemKaydi.objects.filter(eylem=Eylem.GIRIS).exists()


def test_cihazi_olmayan_kullanici_kuruluma_gider(client, kullanici_yap):
    kullanici_yap(Rol.EDITOR, email="yeni@ornek.org")
    assert sifreyle_gir(client, "yeni@ornek.org")["Location"] == KURULUM
    assert client.get(ANA)["Location"] == KURULUM
    assert client.get(IKI_ADIM)["Location"] == KURULUM


def test_sifre_ve_kodla_tam_giris(client, editor):
    sifreyle_gir(client, "Editor@Ornek.org")
    yanit = client.post(IKI_ADIM, {"kod": guncel_kod(cihazi(editor))})
    assert yanit["Location"] == ANA
    assert client.get(ANA).status_code == 200
    kayit = IslemKaydi.objects.get(eylem=Eylem.GIRIS)
    assert kayit.kullanici == editor


def test_hatali_kod_reddedilir_ve_kaydedilir(client, editor):
    sifreyle_gir(client, "editor@ornek.org")
    yanit = client.post(IKI_ADIM, {"kod": "000000" if guncel_kod(cihazi(editor)) != "000000" else "111111"})
    assert yanit.status_code == 200
    assert "Kod hatalı" in yanit.content.decode()
    assert client.get(ANA)["Location"] == IKI_ADIM
    kayit = IslemKaydi.objects.get(eylem=Eylem.BASARISIZ_GIRIS)
    assert kayit.kullanici == editor and kayit.ayrinti == {"asama": "iki_adim"}


def test_hatali_sifre_kisisel_veri_olmadan_kaydedilir(client, editor):
    yanit = sifreyle_gir(client, "editor@ornek.org", "yanlis-sifre-000")
    assert yanit.status_code == 200
    kayit = IslemKaydi.objects.get(eylem=Eylem.BASARISIZ_GIRIS)
    assert kayit.kullanici == editor and kayit.ayrinti == {"asama": "sifre"}


def test_bes_hatali_sifrede_hesap_kilitlenir(client, editor):
    for i in range(5):
        # Büyük/küçük harf ve tarayıcı değiştirmek kilidi atlatmaz.
        sifreyle_gir(client, "EDITOR@ornek.org" if i % 2 else "editor@ornek.org", "yanlis-sifre-000", HTTP_USER_AGENT=f"t{i}")
    yanit = sifreyle_gir(client, "editor@ornek.org", HTTP_USER_AGENT="baska-tarayici")
    assert yanit.status_code == 429
    assert "kilitli" in yanit.content.decode()
    assert not client.session.get("_auth_user_id")


def test_kilit_ip_saklamaz(client, editor):
    from axes.models import AccessAttempt

    for _ in range(5):
        sifreyle_gir(client, "editor@ornek.org", "yanlis-sifre-000", REMOTE_ADDR="203.0.113.7")
    assert AccessAttempt.objects.exists()
    assert not AccessAttempt.objects.exclude(ip_address=None).exists()


def test_dort_hatadan_sonra_dogru_giris_sayaci_sifirlar(client, editor):
    for _ in range(4):
        sifreyle_gir(client, "editor@ornek.org", "yanlis-sifre-000")
    assert sifreyle_gir(client, "editor@ornek.org").status_code == 302
    client.post(reverse("panel:cikis"))
    for _ in range(4):
        sifreyle_gir(client, "editor@ornek.org", "yanlis-sifre-000")
    assert sifreyle_gir(client, "editor@ornek.org").status_code == 302


def test_yeni_cihazdan_giriste_eposta_gider_bilinen_cihazda_gitmez(client, editor):
    sifreyle_gir(client, "editor@ornek.org")
    client.post(IKI_ADIM, {"kod": guncel_kod(cihazi(editor))})
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["editor@ornek.org"]
    assert "yeni bir cihaz" in mail.outbox[0].body
    assert IslemKaydi.objects.filter(eylem=Eylem.YENI_CIHAZ_GIRISI, kullanici=editor).count() == 1

    client.post(reverse("panel:cikis"))
    TOTPDevice.objects.filter(pk=cihazi(editor).pk).update(last_t=-1)
    sifreyle_gir(client, "editor@ornek.org")
    client.post(IKI_ADIM, {"kod": guncel_kod(cihazi(editor))})
    assert client.get(ANA).status_code == 200
    assert len(mail.outbox) == 1


def test_sahte_cihaz_cerezi_uyariyi_engellemez(client, editor):
    client.cookies["diyak_cihaz"] = str(editor.pk)
    sifreyle_gir(client, "editor@ornek.org")
    client.post(IKI_ADIM, {"kod": guncel_kod(cihazi(editor))})
    assert len(mail.outbox) == 1


def test_kurulum_cihazi_onaylar_ve_giris_yapar(client, kullanici_yap):
    k = kullanici_yap(Rol.EDITOR, email="yeni@ornek.org")
    sifreyle_gir(client, "yeni@ornek.org")
    yanit = client.get(KURULUM)
    assert yanit.status_code == 200
    icerik = yanit.content.decode()
    assert "data:image/png;base64," in icerik
    cihaz = TOTPDevice.objects.get(user=k, confirmed=False)
    assert client.get(KURULUM) and TOTPDevice.objects.filter(user=k).count() == 1

    yanit = client.post(KURULUM, {"kod": guncel_kod(cihaz)})
    assert yanit["Location"] == ANA
    cihaz.refresh_from_db()
    assert cihaz.confirmed
    assert client.get(ANA).status_code == 200
    assert mail.outbox == []  # ilk kurulumda "yeni cihaz" uyarısı gönderilmez


def test_onayli_cihazi_olan_kurulumu_acamaz(client, editor):
    sifreyle_gir(client, "editor@ornek.org")
    assert client.get(KURULUM)["Location"] == IKI_ADIM
    assert TOTPDevice.objects.filter(user=editor).count() == 1


def test_giris_yapmamis_kisi_2fa_ekranlarini_acamaz(client):
    for adres in (IKI_ADIM, KURULUM):
        yanit = client.get(adres)
        assert yanit.status_code == 302 and yanit["Location"].startswith(GIRIS)


def test_rolu_olmayan_dogrulanmis_kullanici_panele_giremez(client, kullanici_yap, tam_giris):
    tam_giris(kullanici_yap(email="rolsuz@ornek.org"))
    assert client.get(ANA).status_code == 403


def test_suresi_dolmus_rolle_panele_girilemez(client, kullanici_yap, tam_giris):
    dun = timezone.localdate() - timedelta(days=1)
    tam_giris(kullanici_yap(Rol.YONETIM_KURULU, "Başkan", baslangic=dun - timedelta(days=200), bitis=dun))
    assert client.get(ANA).status_code == 403


def test_kapatilmis_hesap_giris_yapamaz(client, editor):
    editor.is_active = False
    editor.save()
    yanit = sifreyle_gir(client, "editor@ornek.org")
    assert yanit.status_code == 200 and not client.session.get("_auth_user_id")


def test_dis_adrese_yonlendirme_yapilmaz(client, editor):
    client.post(GIRIS + "?next=https://kotu.example/", {"username": "editor@ornek.org", "password": SIFRE})
    yanit = client.post(IKI_ADIM, {"kod": guncel_kod(cihazi(editor))})
    assert yanit["Location"] == ANA


def test_ic_adrese_yonlendirme_korunur(client, editor):
    client.post(GIRIS + "?next=/giris/", {"username": "editor@ornek.org", "password": SIFRE})
    yanit = client.post(IKI_ADIM, {"kod": guncel_kod(cihazi(editor))})
    assert yanit["Location"] == "/giris/"


def test_cikis_yalnizca_post(client, editor, tam_giris):
    tam_giris(editor)
    assert client.get(reverse("panel:cikis")).status_code == 405
    assert client.post(reverse("panel:cikis"))["Location"] == GIRIS
    assert client.get(ANA).status_code == 302
