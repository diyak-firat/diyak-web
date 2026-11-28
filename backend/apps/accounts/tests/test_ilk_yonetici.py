from datetime import timedelta
from io import StringIO

import pytest
from django.core import mail
from django.core.management import CommandError, call_command
from django.utils import timezone

from apps.accounts import servisler
from apps.accounts.models import GOREV_BASKAN, Davet, Rol

pytestmark = pytest.mark.django_db


def calistir(*args) -> str:
    cikti = StringIO()
    call_command("ilk_yonetici", *args, stdout=cikti)
    return cikti.getvalue()


def bitis() -> str:
    return (timezone.localdate() + timedelta(days=300)).isoformat()


def test_ilk_baskan_daveti_olusur_ve_eposta_gider():
    cikti = calistir("Baskan@Firat.edu.tr", "--bitis", bitis())
    davet = Davet.objects.get()
    assert (davet.eposta, davet.rol, davet.gorev_adi, davet.davet_eden) == (
        "baskan@firat.edu.tr",
        Rol.YONETIM_KURULU,
        GOREV_BASKAN,
        None,
    )
    assert "/davet/" in cikti
    assert len(mail.outbox) == 1 and "/davet/" in mail.outbox[0].body


def test_etkin_baskan_varken_calismaz(baskan):
    with pytest.raises(CommandError, match="Başkan zaten var"):
        calistir("ikinci@ornek.org", "--bitis", bitis())
    assert not Davet.objects.exists()


def test_teknik_daveti(baskan):
    cikti = calistir("teknik@firat.edu.tr", "--bitis", bitis(), "--teknik", "--eposta-gonderme")
    assert Davet.objects.get().rol == Rol.TEKNIK
    assert mail.outbox == [] and "/davet/" in cikti


def test_etkin_teknik_varken_teknik_daveti_olmaz(teknik):
    with pytest.raises(CommandError):
        calistir("t2@ornek.org", "--bitis", bitis(), "--teknik")


@pytest.mark.parametrize("tarih", ["31.10.2027", "2020-01-01"])
def test_hatali_veya_gecmis_tarih(tarih):
    with pytest.raises(CommandError):
        calistir("a@ornek.org", "--bitis", tarih)


def test_ilk_davetle_acilan_baskan_davet_edebilir():
    _, token = servisler.ilk_davet_olustur("baskan@ornek.org", timezone.localdate() + timedelta(days=30))
    k = servisler.daveti_kullan(token, "uzun-ve-guclu-sifre-2026")
    yeni, _ = servisler.davet_olustur(k, "uye@ornek.org", Rol.EDITOR, timezone.localdate() + timedelta(days=30))
    assert yeni.davet_eden == k
