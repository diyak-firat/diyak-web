"""Gece görevlerinin hesap ve kayıt kısmı (PANEL.md §8 "Gece görevleri").

Bitiş tarihi geçen roller ayrıca etkisizleştirilmez: yetki sorguları tarihe bakar, süresi dolan
atama kendiliğinden yetki vermez. Burada yalnızca hatırlatma ve eski kayıtların silinmesi yapılır.
"""

from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from apps.denetim.models import IslemKaydi

from .models import ATAMA_YETKILI_GOREVLER, Davet, Rol, RolAtamasi

HATIRLATMA_GUNLERI = (14, 3)  # bitişten bu kadar gün önce Başkan ve Yardımcısı'na e-posta
ISLEM_KAYDI_SAKLAMA = timedelta(days=365)
KULLANILMAMIS_DAVET_SAKLAMA = timedelta(days=7)  # süresi dolduktan sonra
KULLANILMIS_DAVET_SAKLAMA = timedelta(days=365)
ONAYSIZ_CIHAZ_SAKLAMA = timedelta(days=7)


def rol_hatirlatmasi_gonder(bugun=None) -> int:
    """Rolü tam 14 veya 3 gün sonra bitecek kişiler için etkin Başkan ve Başkan Yardımcısı'na
    tek bir e-posta gönderir. Gönderilen e-posta sayısını döndürür.

    Görev her gün çalıştığı için aynı atama için en fazla iki hatırlatma gider.
    """
    bugun = bugun or timezone.localdate()
    gunler = [bugun + timedelta(days=g) for g in HATIRLATMA_GUNLERI]
    bitenler = list(
        RolAtamasi.objects.etkin(bugun).filter(bitis__in=gunler).select_related("kullanici").order_by("bitis", "rol")
    )
    if not bitenler:
        return 0
    alicilar = sorted(
        set(
            RolAtamasi.objects.etkin(bugun)
            .filter(rol=Rol.YONETIM_KURULU, gorev_adi__in=ATAMA_YETKILI_GOREVLER)
            .values_list("kullanici__email", flat=True)
        )
    )
    if not alicilar:
        return 0
    metin = render_to_string(
        "panel/eposta/rol_hatirlatma.txt",
        {"bitenler": bitenler, "panel_adresi": settings.PANEL_ADRESI},
    )
    send_mail(f"DİYAK Panel: {len(bitenler)} rolün süresi yakında doluyor", metin, None, alicilar)
    return 1


def eski_kayitlari_sil(simdi=None) -> dict[str, int]:
    """Saklama süresi dolan kayıtları siler (KVKK: gereğinden uzun tutulmaz)."""
    from axes.models import AccessAttempt
    from django_otp.plugins.otp_totp.models import TOTPDevice

    simdi = simdi or timezone.now()
    sonuc = {
        "islem_kaydi": IslemKaydi.objects.filter(zaman__lt=simdi - ISLEM_KAYDI_SAKLAMA).delete()[0],
        "kullanilmamis_davet": Davet.objects.filter(
            kullanildi__isnull=True, olusturma__lt=simdi - Davet.GECERLILIK - KULLANILMAMIS_DAVET_SAKLAMA
        ).delete()[0],
        "kullanilmis_davet": Davet.objects.filter(kullanildi__lt=simdi - KULLANILMIS_DAVET_SAKLAMA).delete()[0],
        "onaysiz_cihaz": TOTPDevice.objects.filter(
            confirmed=False, created_at__lt=simdi - ONAYSIZ_CIHAZ_SAKLAMA
        ).delete()[0],
        "giris_denemesi": AccessAttempt.objects.filter(attempt_time__lt=simdi - settings.AXES_COOLOFF_TIME).delete()[0],
    }
    return sonuc
