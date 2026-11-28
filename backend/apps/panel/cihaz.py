"""Yeni cihaz uyarısı (PANEL.md §9).

Tarayıcıya imzalı, uzun ömürlü bir çerez bırakılır: bu tarayıcıdan tam giriş (şifre + 2FA)
yapmış kullanıcıların kimlikleri. Listede olmayan bir kullanıcı giriş yaparsa ona e-posta gider.
Sunucuda cihaz bilgisi veya IP saklanmaz.
"""

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from apps.denetim.kayit import kaydet
from apps.denetim.models import Eylem

CEREZ = "diyak_cihaz"
TUZ = "panel.cihaz"
OMUR = 365 * 24 * 60 * 60


def _bilinenler(request) -> list[int]:
    try:
        deger = request.get_signed_cookie(CEREZ, salt=TUZ, max_age=OMUR)
        return [int(x) for x in deger.split(",") if x]
    except (KeyError, signing.BadSignature, ValueError):
        return []


def cihazi_tani(request, response, kullanici, uyar: bool = True) -> None:
    """Tam girişten sonra çağrılır. Bu tarayıcı kullanıcı için yeniyse uyarır ve çerezi günceller."""
    bilinenler = _bilinenler(request)
    if kullanici.pk in bilinenler:
        return
    if uyar:
        kaydet(Eylem.YENI_CIHAZ_GIRISI, kullanici=kullanici)
        metin = render_to_string(
            "panel/eposta/yeni_cihaz.txt",
            {"kullanici": kullanici, "zaman": timezone.localtime(), "panel_adresi": settings.PANEL_ADRESI},
        )
        send_mail("DİYAK Panel: yeni cihazdan giriş", metin, None, [kullanici.email])
    bilinenler = (bilinenler + [kullanici.pk])[-10:]
    response.set_signed_cookie(
        CEREZ,
        ",".join(str(x) for x in bilinenler),
        salt=TUZ,
        max_age=OMUR,
        secure=settings.SESSION_COOKIE_SECURE,
        httponly=True,
        samesite="Lax",
    )
