"""Oturum süreleri: 1 saat hareketsizlik, en fazla 8 saat (PANEL.md §9)."""

import time

import pytest
from django.urls import reverse

from apps.accounts.models import Rol
from apps.panel.middleware import GIRIS_ZAMANI, SON_ETKINLIK

pytestmark = pytest.mark.django_db
ANA = reverse("panel:ana")


@pytest.fixture
def girisli(client, kullanici_yap, tam_giris):
    tam_giris(kullanici_yap(Rol.EDITOR))
    assert client.get(ANA).status_code == 200
    return client


def zamani_kaydir(client, giris_once: int, son_once: int):
    oturum = client.session
    simdi = int(time.time())
    oturum[GIRIS_ZAMANI] = simdi - giris_once
    oturum[SON_ETKINLIK] = simdi - son_once
    oturum.save()


def test_bir_saat_hareketsizlikte_oturum_biter(girisli):
    zamani_kaydir(girisli, 2 * 3600, 3601)
    yanit = girisli.get(ANA)
    assert yanit.status_code == 302 and yanit["Location"].startswith(reverse("panel:giris"))
    assert "süresi doldu" in girisli.get(reverse("panel:giris")).content.decode()


def test_sekiz_saatte_oturum_biter(girisli):
    zamani_kaydir(girisli, 8 * 3600 + 1, 10)
    assert girisli.get(ANA).status_code == 302


def test_etkin_oturum_devam_eder(girisli):
    zamani_kaydir(girisli, 7 * 3600, 3500)
    assert girisli.get(ANA).status_code == 200
    assert girisli.session[SON_ETKINLIK] >= int(time.time()) - 5
