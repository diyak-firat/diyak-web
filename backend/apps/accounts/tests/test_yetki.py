"""Rol atamalarının yetki kuralları (PANEL.md §4, §12 A1 kabul ölçütleri)."""

from datetime import timedelta

import pytest
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
from django.utils import timezone

from apps.accounts import yetki
from apps.accounts.models import GOREV_BASKAN_YARDIMCISI, Rol, RolAtamasi

pytestmark = pytest.mark.django_db
BUGUN = timezone.localdate


def test_etkin_rol_yetki_verir(kullanici_yap):
    k = kullanici_yap(Rol.EDITOR)
    assert yetki.etkin_roller(k) == {Rol.EDITOR}
    assert yetki.panel_kullanicisi_mi(k)


def test_suresi_dolmus_rol_hicbir_yetki_vermez(kullanici_yap):
    dun = BUGUN() - timedelta(days=1)
    k = kullanici_yap(Rol.YONETIM_KURULU, "Başkan", baslangic=dun - timedelta(days=300), bitis=dun)
    assert yetki.etkin_roller(k) == set()
    assert not yetki.panel_kullanicisi_mi(k)
    assert not yetki.baskan_veya_yardimcisi_mi(k)
    assert yetki.atanabilir_roller(k) == frozenset()


def test_bitis_gunu_dahildir(kullanici_yap):
    k = kullanici_yap(Rol.EDITOR, bitis=BUGUN())
    assert yetki.rolu_var(k, Rol.EDITOR)
    assert not yetki.rolu_var(k, Rol.EDITOR, gun=BUGUN() + timedelta(days=1))


def test_henuz_baslamamis_rol_yetki_vermez(kullanici_yap):
    yarin = BUGUN() + timedelta(days=1)
    k = kullanici_yap(Rol.EDITOR, baslangic=yarin, bitis=yarin + timedelta(days=30))
    assert not yetki.panel_kullanicisi_mi(k)


def test_kapatilmis_hesabin_rolu_yetki_vermez(kullanici_yap):
    k = kullanici_yap(Rol.YONETIM_KURULU, "Başkan")
    k.is_active = False
    k.save()
    assert yetki.etkin_roller(k) == set()
    assert not yetki.baskan_veya_yardimcisi_mi(k)


def test_superuser_panelde_yetki_tasimaz(db):
    from django.contrib.auth import get_user_model

    k = get_user_model().objects.create_superuser(email="su@ornek.org", password="x" * 12)
    assert not yetki.panel_kullanicisi_mi(k)
    assert yetki.atanabilir_roller(k) == frozenset()


def test_giris_yapmamis_kisinin_yetkisi_yok():
    anonim = AnonymousUser()
    assert yetki.etkin_roller(anonim) == set()
    assert not yetki.kullanicilari_yonetebilir_mi(anonim)
    assert not yetki.kullanicilari_yonetebilir_mi(None)


def test_baskan_ve_yardimcisi_teknik_disindaki_rolleri_atar(baskan, kullanici_yap):
    yrd = kullanici_yap(Rol.YONETIM_KURULU, GOREV_BASKAN_YARDIMCISI)
    for k in (baskan, yrd):
        assert yetki.atanabilir_roller(k) == {Rol.YONETIM_KURULU, Rol.EDITOR, Rol.DANISMAN}
        assert yetki.kullanicilari_yonetebilir_mi(k)


@pytest.mark.parametrize(
    "rol,gorev",
    [(Rol.YONETIM_KURULU, ""), (Rol.YONETIM_KURULU, "Sayman"), (Rol.EDITOR, "Başkan"), (Rol.DANISMAN, ""), (Rol.EDITOR, "")],
)
def test_baskanlik_disindaki_roller_atama_yapamaz(kullanici_yap, rol, gorev):
    k = kullanici_yap(rol, gorev)
    assert yetki.atanabilir_roller(k) == frozenset()
    assert not yetki.kullanicilari_yonetebilir_mi(k)


def test_teknik_yalnizca_teknik_rolunu_atar(teknik):
    assert yetki.atanabilir_roller(teknik) == {Rol.TEKNIK}


def test_bitis_baslangictan_once_olamaz(kullanici_yap):
    k = kullanici_yap()
    with pytest.raises(IntegrityError):
        RolAtamasi.objects.create(kullanici=k, rol=Rol.EDITOR, baslangic=BUGUN(), bitis=BUGUN() - timedelta(days=1))
