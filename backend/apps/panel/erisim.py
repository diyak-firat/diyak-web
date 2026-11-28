"""Panel görünümlerinin erişim denetimi. Her panel görünümü ``panel_gerekli`` ile sarılır.

Sıra: giriş yapılmış mı → 2FA doğrulanmış mı → etkin bir rolü var mı → (varsa) ek koşul.
"""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django_otp import devices_for_user

from apps.accounts.yetki import panel_kullanicisi_mi


def onayli_cihazi_var(kullanici) -> bool:
    return any(True for _ in devices_for_user(kullanici, confirmed=True))


def ikinci_adim_adresi(kullanici) -> str:
    return "panel:iki_adim" if onayli_cihazi_var(kullanici) else "panel:kurulum"


def panel_gerekli(kosul=None):
    """Panel görünümü dekoratörü. ``kosul(kullanici) -> bool`` ek yetki denetimi içindir."""

    def dekorator(gorunum):
        @wraps(gorunum)
        def sarici(request, *args, **kwargs):
            k = request.user
            if not k.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not k.is_verified():
                return redirect(ikinci_adim_adresi(k))
            if not panel_kullanicisi_mi(k):
                raise PermissionDenied
            if kosul is not None and not kosul(k):
                raise PermissionDenied
            return gorunum(request, *args, **kwargs)

        return sarici

    return dekorator
