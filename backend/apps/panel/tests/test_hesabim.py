import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client
from django.urls import reverse

from apps.accounts.models import Rol
from apps.denetim.kayit import kaydet
from apps.denetim.models import Eylem, IslemKaydi
from conftest import SIFRE, dogrulanmis_giris

pytestmark = pytest.mark.django_db
HESABIM = reverse("panel:hesabim")
SIFRE_ADRESI = reverse("panel:hesabim_sifre")
YENI = "baska-uzun-guclu-sifre-2027"


@pytest.fixture
def editor(kullanici_yap):
    return kullanici_yap(Rol.EDITOR, email="editor@ornek.org")


def test_giris_yapmamis_ve_dogrulanmamis_giremez(client, editor):
    for adres in (HESABIM, SIFRE_ADRESI):
        assert client.get(adres)["Location"].startswith(reverse("panel:giris"))
    client.force_login(editor)
    for adres in (HESABIM, SIFRE_ADRESI):
        assert client.get(adres)["Location"] == reverse("panel:kurulum")


def test_rolsuz_ve_suresi_dolmus_giremez(client, kullanici_yap, tam_giris):
    tam_giris(kullanici_yap())
    assert client.get(HESABIM).status_code == 403
    assert client.post(SIFRE_ADRESI, {"old_password": SIFRE, "new_password1": YENI, "new_password2": YENI}).status_code == 403


def test_hesabim_yalnizca_kendi_olaylarini_gosterir(client, tam_giris, editor, kullanici_yap):
    baska = kullanici_yap(Rol.EDITOR)
    kaydet(Eylem.BASARISIZ_GIRIS, kullanici=editor, ayrinti={"asama": "sifre"})
    kaydet(Eylem.GIRIS, kullanici=baska)
    tam_giris(editor)
    yanit = client.get(HESABIM)
    assert yanit.status_code == 200
    assert [o.kullanici for o in yanit.context["olaylar"]] == [editor]
    assert "(şifre)" in yanit.content.decode()
    assert reverse("panel:hesabim") in yanit.content.decode()  # menüde


def test_sifre_degistirme_diger_oturumlari_kapatir(client, tam_giris, editor):
    diger = Client()
    dogrulanmis_giris(diger, editor)
    tam_giris(editor)
    yanit = client.post(SIFRE_ADRESI, {"old_password": SIFRE, "new_password1": YENI, "new_password2": YENI})
    assert yanit["Location"] == HESABIM
    editor.refresh_from_db()
    assert editor.check_password(YENI)
    assert client.get(HESABIM).status_code == 200
    assert diger.get(HESABIM).status_code == 302
    assert IslemKaydi.objects.filter(eylem=Eylem.SIFRE_DEGISTIRME, kullanici=editor).exists()
    assert len(mail.outbox) == 1 and "şifresi" in mail.outbox[0].body


@pytest.mark.parametrize(
    "eski,yeni1,yeni2",
    [("yanlis-mevcut-sifre", YENI, YENI), (SIFRE, "kisa", "kisa"), (SIFRE, YENI, YENI + "x")],
)
def test_hatali_sifre_degisikligi_reddedilir(client, tam_giris, editor, eski, yeni1, yeni2):
    tam_giris(editor)
    yanit = client.post(SIFRE_ADRESI, {"old_password": eski, "new_password1": yeni1, "new_password2": yeni2})
    assert yanit.status_code == 200
    assert get_user_model().objects.get(pk=editor.pk).check_password(SIFRE)
    assert mail.outbox == []
