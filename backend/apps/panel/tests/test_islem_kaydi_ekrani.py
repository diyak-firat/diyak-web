from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Rol
from apps.denetim.kayit import kaydet
from apps.denetim.models import Eylem

pytestmark = pytest.mark.django_db
ADRES = reverse("panel:islem_kaydi")


def test_giris_yapmamis_ve_dogrulanmamis_giremez(client, baskan):
    assert client.get(ADRES)["Location"].startswith(reverse("panel:giris"))
    client.force_login(baskan)
    assert client.get(ADRES)["Location"] == reverse("panel:kurulum")


@pytest.mark.parametrize("rol", [None, Rol.EDITOR])
def test_editor_ve_rolsuz_403(client, kullanici_yap, tam_giris, rol):
    tam_giris(kullanici_yap(rol))
    assert client.get(ADRES).status_code == 403
    assert ADRES not in client.get(reverse("panel:hesabim")).content.decode()


def test_suresi_dolmus_danisman_403(client, kullanici_yap, tam_giris):
    dun = timezone.localdate() - timedelta(days=1)
    tam_giris(kullanici_yap(Rol.DANISMAN, baslangic=dun - timedelta(days=100), bitis=dun))
    assert client.get(ADRES).status_code == 403


@pytest.mark.parametrize("rol,gorev", [(Rol.YONETIM_KURULU, "Sayman"), (Rol.DANISMAN, ""), (Rol.TEKNIK, "")])
def test_yetkili_roller_gorur(client, kullanici_yap, tam_giris, rol, gorev):
    k = tam_giris(kullanici_yap(rol, gorev))
    kaydet(Eylem.GIRIS, kullanici=k)
    yanit = client.get(ADRES)
    assert yanit.status_code == 200 and "Giriş" in yanit.content.decode()
    assert ADRES in yanit.content.decode()  # menüde


def test_filtreler(client, tam_giris, baskan, kullanici_yap):
    diger = kullanici_yap(Rol.EDITOR)
    kaydet(Eylem.GIRIS, kullanici=baskan)
    kaydet(Eylem.BASARISIZ_GIRIS, kullanici=diger, ayrinti={"asama": "sifre"})
    tam_giris(baskan)
    assert [k.eylem for k in client.get(ADRES, {"eylem": Eylem.BASARISIZ_GIRIS}).context["sayfa"]] == [Eylem.BASARISIZ_GIRIS]
    assert {k.kullanici for k in client.get(ADRES, {"kisi": diger.pk}).context["sayfa"]} == {diger}
    # Geçersiz filtre değerleri yok sayılır, hata vermez.
    assert client.get(ADRES, {"eylem": "<x>", "kisi": "abc", "sayfa": "999"}).status_code == 200


def test_ekran_yalnizca_okur(client, tam_giris, baskan):
    tam_giris(baskan)
    assert client.post(ADRES).status_code == 405
