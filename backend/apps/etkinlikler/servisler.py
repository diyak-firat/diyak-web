"""Etkinlik işlemleri.

Düzenleme kuralı duyurularla aynıdır: yayındaki (veya onay bekleyen) bir duyuruya bağlı etkinliğin
zamanı ve yeri sitede görünür; bu yüzden onu yalnızca Yönetim Kurulu değiştirir ve değişiklik
işlem kaydına "yayımlama" olarak düşer. Diğer etkinlikleri Editör ve Yönetim Kurulu düzenler.
"""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from apps.accounts.yetki import icerik_hazirlayabilir_mi, onaylayabilir_mi
from apps.denetim.kayit import kaydet
from apps.denetim.models import Eylem

from .models import Etkinlik

ALANLAR = ("ad", "aciklama", "baslangic", "bitis", "yer", "cevrim_ici", "harita_baglantisi")


def _yayina_bagli(etkinlik: Etkinlik) -> bool:
    from apps.duyurular.models import Durum

    return etkinlik.pk is not None and etkinlik.duyurular.filter(durum__in=[Durum.YAYINDA, Durum.ONAY_BEKLIYOR]).exists()


def duzenleyebilir_mi(kullanici, etkinlik: Etkinlik | None = None) -> bool:
    if etkinlik is not None and _yayina_bagli(etkinlik):
        return onaylayabilir_mi(kullanici)
    return icerik_hazirlayabilir_mi(kullanici)


def kaydet_etkinlik(kullanici, veri: dict, etkinlik: Etkinlik | None = None) -> Etkinlik:
    if not duzenleyebilir_mi(kullanici, etkinlik):
        raise PermissionDenied("Bu etkinliği düzenleme yetkiniz yok.")
    with transaction.atomic():
        yayindaydi = etkinlik is not None and _yayina_bagli(etkinlik)
        if etkinlik is None:
            etkinlik = Etkinlik(olusturan=kullanici)
        for alan in ALANLAR:
            if alan in veri:
                setattr(etkinlik, alan, veri[alan])
        etkinlik.full_clean(exclude=["olusturan"])
        etkinlik.save()
        if yayindaydi:
            kaydet(Eylem.YAYIMLAMA, kullanici=kullanici, nesne=etkinlik, ayrinti={"yayindaki_duzenleme": True})
    return etkinlik


def silinebilir_mi(etkinlik: Etkinlik) -> bool:
    """Hiçbir duyuruya bağlı olmayan etkinlik silinebilir (A4'te: formu olmayan)."""
    return not etkinlik.duyurular.exists()


def sil(kullanici, etkinlik: Etkinlik) -> None:
    if not icerik_hazirlayabilir_mi(kullanici):
        raise PermissionDenied("Etkinlik silme yetkiniz yok.")
    if not silinebilir_mi(etkinlik):
        raise ValidationError("Bu etkinlik bir duyuruya bağlı; önce duyurudan ayırın.")
    etkinlik.delete()
