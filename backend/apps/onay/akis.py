"""Ortak onay akışı (PANEL.md §8): taslak → onay bekliyor → (Yönetim Kurulu) onay.

Duyuru, form ve ekip değişikliği aynı akışı kullanır. Nesnede şunlar bulunur:
``durum`` ("taslak", "onay_bekliyor", ...), ``olusturan``, ``onaylayan``, ``onay_notu``,
``eksikler() -> list[str]`` ve onay anındaki türe özgü geçiş için ``onaylaninca(simdi)``.

Kurallar:
- Onay yalnızca etkin Yönetim Kurulu rolüyle verilir. Kendi içeriğini onaylamak serbesttir ama
  işlem kaydında ``kendi_icerigi`` olarak görünür.
- E-postadaki bağlantı onay vermez; bu fonksiyonlar yalnızca panelin POST görünümlerinden çağrılır.
"""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.yetki import icerik_hazirlayabilir_mi, onaylayabilir_mi
from apps.denetim.kayit import kaydet
from apps.denetim.models import Eylem

TASLAK = "taslak"
ONAY_BEKLIYOR = "onay_bekliyor"


def _kilitle(nesne):
    """Aynı nesne için eşzamanlı iki işlemi (ör. iki onay) sıraya sokar."""
    return type(nesne).objects.select_for_update().get(pk=nesne.pk)


def onaya_gonder(kullanici, nesne):
    if not icerik_hazirlayabilir_mi(kullanici):
        raise PermissionDenied("Onaya gönderme yetkiniz yok.")
    with transaction.atomic():
        nesne = _kilitle(nesne)
        if nesne.durum != TASLAK:
            raise ValidationError("Yalnızca taslak onaya gönderilebilir.")
        if eksikler := nesne.eksikler():
            raise ValidationError(eksikler)
        nesne.durum = ONAY_BEKLIYOR
        nesne.onay_notu = ""
        nesne.save()
        kaydet(Eylem.ONAYA_GONDERME, kullanici=kullanici, nesne=nesne)
    return nesne


def onayla(kullanici, nesne):
    if not onaylayabilir_mi(kullanici):
        raise PermissionDenied("Onay yalnızca Yönetim Kurulu üyesi tarafından verilir.")
    with transaction.atomic():
        nesne = _kilitle(nesne)
        if nesne.durum != ONAY_BEKLIYOR:
            raise ValidationError("Bu içerik onay beklemiyor.")
        if eksikler := nesne.eksikler():
            raise ValidationError(eksikler)
        nesne.onaylayan = kullanici
        nesne.onay_notu = ""
        nesne.onaylaninca(timezone.now())
        nesne.save()
        ayrinti = {"kendi_icerigi": True} if nesne.olusturan_id == kullanici.pk else {}
        kaydet(Eylem.ONAYLAMA, kullanici=kullanici, nesne=nesne, ayrinti=ayrinti)
    return nesne


def duzeltme_iste(kullanici, nesne, not_: str):
    if not onaylayabilir_mi(kullanici):
        raise PermissionDenied("Düzeltme isteği yalnızca Yönetim Kurulu üyesi tarafından verilir.")
    not_ = (not_ or "").strip()
    if not not_:
        raise ValidationError({"not": "Neyin düzeltilmesi gerektiğini yazın."})
    with transaction.atomic():
        nesne = _kilitle(nesne)
        if nesne.durum != ONAY_BEKLIYOR:
            raise ValidationError("Bu içerik onay beklemiyor.")
        nesne.durum = TASLAK
        nesne.onay_notu = not_[:2000]
        nesne.save()
        kaydet(Eylem.DUZELTME_ISTEME, kullanici=kullanici, nesne=nesne)
    return nesne


def geri_cek(kullanici, nesne):
    """Onay bekleyen içeriği hazırlayanı veya bir Yönetim Kurulu üyesi taslağa geri alır."""
    if not (nesne.olusturan_id == kullanici.pk and icerik_hazirlayabilir_mi(kullanici)) and not onaylayabilir_mi(kullanici):
        raise PermissionDenied("Bu içeriği geri çekme yetkiniz yok.")
    with transaction.atomic():
        nesne = _kilitle(nesne)
        if nesne.durum != ONAY_BEKLIYOR:
            raise ValidationError("Bu içerik onay beklemiyor.")
        nesne.durum = TASLAK
        nesne.save()
    return nesne
