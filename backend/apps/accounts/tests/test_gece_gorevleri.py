from datetime import timedelta
from io import StringIO

import pytest
from django.core import mail
from django.core.management import call_command
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts import servisler
from apps.accounts.bakim import eski_kayitlari_sil, rol_hatirlatmasi_gonder
from apps.accounts.models import GOREV_BASKAN_YARDIMCISI, Davet, Rol
from apps.denetim.kayit import kaydet
from apps.denetim.models import Eylem, IslemKaydi

pytestmark = pytest.mark.django_db
BUGUN = timezone.localdate


def test_14_ve_3_gun_kala_baskanliga_hatirlatma_gider(baskan, kullanici_yap):
    yrd = kullanici_yap(Rol.YONETIM_KURULU, GOREV_BASKAN_YARDIMCISI, email="yrd@ornek.org")
    kullanici_yap(Rol.EDITOR, email="on4@ornek.org", first_name="On", last_name="Dört", bitis=BUGUN() + timedelta(days=14))
    kullanici_yap(Rol.DANISMAN, email="uc@ornek.org", bitis=BUGUN() + timedelta(days=3))
    kullanici_yap(Rol.EDITOR, email="on@ornek.org", bitis=BUGUN() + timedelta(days=10))
    kullanici_yap(Rol.EDITOR, email="sayman@ornek.org")
    assert rol_hatirlatmasi_gonder() == 1
    assert len(mail.outbox) == 1
    e = mail.outbox[0]
    assert sorted(e.to) == sorted([baskan.email, yrd.email])
    assert "On Dört" in e.body and "uc@ornek.org" in e.body
    assert "on@ornek.org" not in e.body and "sayman@ornek.org" not in e.body
    assert e.subject.startswith("DİYAK Panel: 2 rolün")


def test_bitecek_rol_yoksa_eposta_gitmez(baskan):
    assert rol_hatirlatmasi_gonder() == 0 and mail.outbox == []


def test_baskan_yoksa_eposta_gitmez(kullanici_yap):
    kullanici_yap(Rol.EDITOR, bitis=BUGUN() + timedelta(days=14))
    assert rol_hatirlatmasi_gonder() == 0


def test_eski_kayitlar_silinir_yenileri_kalir(baskan, donem_sonu):
    simdi = timezone.now()
    eski = kaydet(Eylem.GIRIS, kullanici=baskan)
    IslemKaydi.objects.filter(pk=eski.pk).update(zaman=simdi - timedelta(days=366))
    yeni = kaydet(Eylem.GIRIS, kullanici=baskan)

    eski_davet, _ = servisler.davet_olustur(baskan, "eski@ornek.org", Rol.EDITOR, donem_sonu)
    Davet.objects.filter(pk=eski_davet.pk).update(olusturma=simdi - timedelta(days=10))
    acik_davet, _ = servisler.davet_olustur(baskan, "acik@ornek.org", Rol.EDITOR, donem_sonu)

    onaysiz = TOTPDevice.objects.create(user=baskan, name="T", confirmed=False)
    TOTPDevice.objects.filter(pk=onaysiz.pk).update(created_at=simdi - timedelta(days=8))
    onayli = TOTPDevice.objects.create(user=baskan, name="T2", confirmed=True)
    TOTPDevice.objects.filter(pk=onayli.pk).update(created_at=simdi - timedelta(days=800))

    sonuc = eski_kayitlari_sil()
    assert sonuc["islem_kaydi"] == 1 and sonuc["kullanilmamis_davet"] == 1 and sonuc["onaysiz_cihaz"] == 1
    assert IslemKaydi.objects.filter(pk=yeni.pk).exists() and not IslemKaydi.objects.filter(pk=eski.pk).exists()
    assert Davet.objects.filter(pk=acik_davet.pk).exists()
    assert TOTPDevice.objects.filter(pk=onayli.pk).exists()


def test_komut_calisir(baskan):
    cikti = StringIO()
    call_command("gece_gorevleri", stdout=cikti)
    assert "rol hatırlatması: 0" in cikti.getvalue()
