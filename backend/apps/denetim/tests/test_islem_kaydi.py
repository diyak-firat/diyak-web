import pytest
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from apps.denetim.kayit import kaydet
from apps.denetim.models import Eylem, IslemKaydi

pytestmark = pytest.mark.django_db


def test_anonim_kullanici_bos_kaydedilir():
    kayit = kaydet(Eylem.BASARISIZ_GIRIS, kullanici=AnonymousUser())
    assert kayit.kullanici is None and kayit.nesne_turu == "" and kayit.ayrinti == {}


def test_nesne_turu_ve_kimligi_yazilir(kullanici_yap):
    k = kullanici_yap()
    kayit = kaydet(Eylem.GIRIS, kullanici=k, nesne=k)
    assert kayit.nesne_turu == "accounts.kullanici" and kayit.nesne_id == str(k.pk)


def test_admin_islem_kaydini_degistiremez_silemez(client, db):
    from django.contrib.auth import get_user_model

    su = get_user_model().objects.create_superuser(email="su@ornek.org", password="x" * 12)
    client.force_login(su)
    kayit = kaydet(Eylem.GIRIS, kullanici=su)
    assert client.get(reverse("admin:denetim_islemkaydi_changelist")).status_code == 200
    assert client.get(reverse("admin:denetim_islemkaydi_add")).status_code == 403
    assert client.post(reverse("admin:denetim_islemkaydi_delete", args=[kayit.pk]), {"post": "yes"}).status_code == 403
    assert IslemKaydi.objects.filter(pk=kayit.pk).exists()


def test_admin_rol_atamasi_ekleyemez(client, db):
    from django.contrib.auth import get_user_model

    su = get_user_model().objects.create_superuser(email="su@ornek.org", password="x" * 12)
    client.force_login(su)
    assert client.get(reverse("admin:accounts_rolatamasi_changelist")).status_code == 200
    assert client.get(reverse("admin:accounts_rolatamasi_add")).status_code == 403
    assert client.get(reverse("admin:accounts_davet_add")).status_code == 403
