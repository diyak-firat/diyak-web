"""Duyuru işlemleri. Yetki ve işlem kaydı burada; görünümler yalnızca bu fonksiyonları çağırır.

Düzenleme kuralı (onaysız hiçbir şey yayına çıkmasın diye):
- Taslak ve yayından kaldırılmış duyuruyu Editör ve Yönetim Kurulu düzenler. Kaldırılmış duyuru
  düzenlenince taslağa döner ve yeniden onaydan geçer.
- Onay bekleyen duyuru düzenlenmez; önce geri çekilir veya düzeltme istenir.
- Yayındaki duyuruyu yalnızca Yönetim Kurulu düzenler (onay yetkisi olan kişi); her düzenleme
  işlem kaydına "yayımlama" olarak düşer.
"""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from apps.accounts.yetki import icerik_hazirlayabilir_mi, onaylayabilir_mi
from apps.denetim.kayit import kaydet
from apps.denetim.models import Eylem
from apps.etkinlikler.models import Etkinlik

from .models import Durum, Duyuru, Etiket

ALANLAR = ("baslik", "etiket", "ozet", "govde")


def duzenleyebilir_mi(kullanici, duyuru: Duyuru | None = None) -> bool:
    if duyuru is None or duyuru.durum in (Durum.TASLAK, Durum.KALDIRILDI):
        return icerik_hazirlayabilir_mi(kullanici)
    if duyuru.durum == Durum.YAYINDA:
        return onaylayabilir_mi(kullanici)
    return False


def _etkinligi_esle(kullanici, duyuru: Duyuru, etkinlik_bilgisi: dict | None, etkinlik: Etkinlik | None) -> None:
    """Etkinlik etiketli duyuruya etkinlik bağlar.

    ``etkinlik`` verilirse var olan etkinlik bağlanır (bilgileri Etkinlikler ekranında düzenlenir).
    Verilmezse ``etkinlik_bilgisi`` ile yeni etkinlik açılır ya da bağlı olan güncellenir.
    """
    if duyuru.etiket != Etiket.ETKINLIK:
        return
    if etkinlik is not None:
        duyuru.etkinlik = etkinlik
        return
    if not etkinlik_bilgisi:
        return
    if duyuru.etkinlik is None:
        duyuru.etkinlik = Etkinlik.objects.create(ad=duyuru.baslik, olusturan=kullanici, **etkinlik_bilgisi)
    else:
        for alan, deger in etkinlik_bilgisi.items():
            setattr(duyuru.etkinlik, alan, deger)
        duyuru.etkinlik.ad = duyuru.baslik
        duyuru.etkinlik.save()


def kaydet_duyuru(
    kullanici, veri: dict, duyuru: Duyuru | None = None, etkinlik_bilgisi: dict | None = None,
    etkinlik: Etkinlik | None = None,
) -> Duyuru:
    """Yeni duyuru oluşturur veya var olanı günceller. ``veri``: baslik, etiket, ozet, govde."""
    if not duzenleyebilir_mi(kullanici, duyuru):
        raise PermissionDenied("Bu duyuruyu düzenleme yetkiniz yok.")
    with transaction.atomic():
        if duyuru is None:
            duyuru = Duyuru(olusturan=kullanici)
        else:
            duyuru = Duyuru.objects.select_for_update().get(pk=duyuru.pk)
            if not duzenleyebilir_mi(kullanici, duyuru):
                raise PermissionDenied("Bu duyuruyu düzenleme yetkiniz yok.")
        for alan in ALANLAR:
            if alan in veri:
                setattr(duyuru, alan, veri[alan])
        _etkinligi_esle(kullanici, duyuru, etkinlik_bilgisi, etkinlik)
        yayindaydi = duyuru.pk is not None and duyuru.durum == Durum.YAYINDA
        if duyuru.durum == Durum.KALDIRILDI:
            duyuru.durum = Durum.TASLAK
        duyuru.save()
        if yayindaydi:
            kaydet(Eylem.YAYIMLAMA, kullanici=kullanici, nesne=duyuru, ayrinti={"yayindaki_duzenleme": True})
    return duyuru


def yayindan_kaldir(kullanici, duyuru: Duyuru) -> Duyuru:
    if not onaylayabilir_mi(kullanici):
        raise PermissionDenied("Yayından kaldırma yalnızca Yönetim Kurulu üyesi tarafından yapılır.")
    with transaction.atomic():
        duyuru = Duyuru.objects.select_for_update().get(pk=duyuru.pk)
        if duyuru.durum != Durum.YAYINDA:
            raise ValidationError("Duyuru yayında değil.")
        duyuru.durum = Durum.KALDIRILDI
        duyuru.save()
        kaydet(Eylem.YAYINDAN_KALDIRMA, kullanici=kullanici, nesne=duyuru)
    return duyuru


def sil(kullanici, duyuru: Duyuru) -> None:
    """Hiç yayımlanmamış taslağı hazırlayanı veya Yönetim Kurulu siler."""
    if duyuru.durum != Durum.TASLAK or duyuru.yayin_tarihi is not None:
        raise ValidationError("Yalnızca hiç yayımlanmamış taslaklar silinebilir.")
    if not (duyuru.olusturan_id == kullanici.pk and icerik_hazirlayabilir_mi(kullanici)) and not onaylayabilir_mi(kullanici):
        raise PermissionDenied("Bu taslağı silme yetkiniz yok.")
    duyuru.delete()
