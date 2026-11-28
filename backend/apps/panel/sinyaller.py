"""Giriş olaylarını işlem kaydına yazar. E-posta veya IP kaydedilmez."""

import time

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

from apps.denetim.kayit import kaydet
from apps.denetim.models import Eylem

from .middleware import GIRIS_ZAMANI, SON_ETKINLIK


@receiver(user_logged_in)
def giris_zamanini_yaz(sender, request, user, **kwargs):
    if request is not None and hasattr(request, "session"):
        simdi = int(time.time())
        request.session[GIRIS_ZAMANI] = request.session[SON_ETKINLIK] = simdi


@receiver(user_login_failed)
def basarisiz_sifre(sender, credentials, request=None, **kwargs):
    eposta = (credentials.get("username") or credentials.get("email") or "").strip()
    kullanici = get_user_model().objects.filter(email__iexact=eposta).first() if eposta else None
    kaydet(Eylem.BASARISIZ_GIRIS, kullanici=kullanici, ayrinti={"asama": "sifre"})
