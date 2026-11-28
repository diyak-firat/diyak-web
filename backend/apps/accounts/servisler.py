"""Davet ve rol atama işlemleri. Yetki denetimi ve işlem kaydı burada yapılır;
görünümler ve yönetim komutları bu fonksiyonları çağırır.
"""

import hashlib
import secrets
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.denetim.kayit import kaydet
from apps.denetim.models import Eylem

from .models import Davet, Rol, RolAtamasi
from .yetki import rol_atayabilir_mi


def _ozet(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _tarihleri_denetle(baslangic: date, bitis: date) -> None:
    if bitis < timezone.localdate():
        raise ValidationError({"bitis": "Bitiş tarihi geçmişte olamaz."})
    if bitis < baslangic:
        raise ValidationError({"bitis": "Bitiş tarihi başlangıçtan önce olamaz."})


def _rol_denetle(rol: str) -> None:
    if rol not in Rol.values:
        raise ValidationError({"rol": "Geçersiz rol."})


def _atama_ayrintisi(atama: RolAtamasi) -> dict:
    return {
        "hedef_kullanici": atama.kullanici_id,
        "rol": atama.rol,
        "gorev_adi": atama.gorev_adi,
        "baslangic": atama.baslangic.isoformat(),
        "bitis": atama.bitis.isoformat(),
    }


def davet_olustur(davet_eden, eposta: str, rol: str, bitis: date, gorev_adi: str = "") -> tuple[Davet, str]:
    """Davet oluşturur ve bağlantıda kullanılacak belirteci döndürür (yalnızca bir kez).

    Aynı e-postaya açılmış, kullanılmamış eski davetler geçersiz kılınır.
    """
    _rol_denetle(rol)
    if not rol_atayabilir_mi(davet_eden, rol):
        raise PermissionDenied("Bu rol için davet gönderme yetkiniz yok.")
    eposta = get_user_model().objects.normalize_email(eposta).lower()
    if get_user_model().objects.filter(email__iexact=eposta).exists():
        raise ValidationError({"eposta": "Bu e-postayla bir hesap zaten var. Rolü Kullanıcılar ekranından atayın."})
    _tarihleri_denetle(timezone.localdate(), bitis)

    token = secrets.token_urlsafe(32)
    with transaction.atomic():
        Davet.objects.filter(eposta__iexact=eposta, kullanildi__isnull=True).delete()
        davet = Davet.objects.create(
            eposta=eposta,
            rol=rol,
            gorev_adi=gorev_adi.strip(),
            bitis=bitis,
            token_ozeti=_ozet(token),
            davet_eden=davet_eden,
        )
        kaydet(
            Eylem.DAVET,
            kullanici=davet_eden,
            nesne=davet,
            ayrinti={"rol": rol, "gorev_adi": davet.gorev_adi, "bitis": bitis.isoformat()},
        )
    return davet, token


def davet_bul(token: str) -> Davet | None:
    """Geçerli (kullanılmamış, süresi dolmamış) daveti döndürür; yoksa ``None``."""
    if not token:
        return None
    davet = Davet.objects.filter(token_ozeti=_ozet(token)).first()
    if davet is None or not davet.gecerli_mi():
        return None
    return davet


def daveti_kullan(token: str, sifre: str, ad: str = "", soyad: str = ""):
    """Daveti kabul eder: hesabı açar, rolü atar, daveti kapatır. Kullanıcıyı döndürür.

    Geçersiz davette ``ValidationError`` verir; nedenini (süresi dolmuş, kullanılmış, hiç
    olmamış) ayırt etmez.
    """
    Kullanici = get_user_model()
    with transaction.atomic():
        davet = Davet.objects.select_for_update().filter(token_ozeti=_ozet(token or "")).first()
        if davet is None or not davet.gecerli_mi():
            raise ValidationError("Davet bağlantısı geçersiz veya süresi dolmuş. Sizi davet eden kişiden yenisini isteyin.")
        if Kullanici.objects.filter(email__iexact=davet.eposta).exists():
            raise ValidationError("Bu e-postayla bir hesap zaten var.")

        kullanici = Kullanici(email=davet.eposta, first_name=ad.strip(), last_name=soyad.strip())
        validate_password(sifre, user=kullanici)
        kullanici.set_password(sifre)
        kullanici.save()

        bugun = timezone.localdate()
        atama = RolAtamasi.objects.create(
            kullanici=kullanici,
            rol=davet.rol,
            gorev_adi=davet.gorev_adi,
            baslangic=bugun,
            bitis=max(davet.bitis, bugun),
            atayan=davet.davet_eden,
        )
        davet.kullanildi = timezone.now()
        davet.save(update_fields=["kullanildi"])

        kaydet(Eylem.DAVET_KABUL, kullanici=kullanici, nesne=davet)
        kaydet(Eylem.ROL_ATAMA, kullanici=davet.davet_eden, nesne=atama, ayrinti=_atama_ayrintisi(atama) | {"kaynak": "davet"})
    return kullanici


def rol_ata(atayan, kullanici, rol: str, bitis: date, gorev_adi: str = "", baslangic: date | None = None) -> RolAtamasi:
    _rol_denetle(rol)
    if not rol_atayabilir_mi(atayan, rol):
        raise PermissionDenied("Bu rolü atama yetkiniz yok.")
    if not kullanici.is_active:
        raise ValidationError("Kapatılmış bir hesaba rol atanamaz.")
    baslangic = baslangic or timezone.localdate()
    _tarihleri_denetle(baslangic, bitis)
    with transaction.atomic():
        atama = RolAtamasi.objects.create(
            kullanici=kullanici, rol=rol, gorev_adi=gorev_adi.strip(), baslangic=baslangic, bitis=bitis, atayan=atayan
        )
        kaydet(Eylem.ROL_ATAMA, kullanici=atayan, nesne=atama, ayrinti=_atama_ayrintisi(atama))
    return atama


def rol_kaldir(kaldiran, atama: RolAtamasi) -> None:
    """Rol atamasını kaldırır. İz işlem kaydında kalır."""
    if not rol_atayabilir_mi(kaldiran, atama.rol):
        raise PermissionDenied("Bu rolü kaldırma yetkiniz yok.")
    with transaction.atomic():
        kaydet(Eylem.ROL_KALDIRMA, kullanici=kaldiran, nesne=atama, ayrinti=_atama_ayrintisi(atama))
        atama.delete()
