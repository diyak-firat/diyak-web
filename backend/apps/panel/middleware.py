"""Oturum süreleri (PANEL.md §9): girişten 8 saat sonra veya 1 saat hareketsizlikte oturum biter."""

import time

from django.conf import settings
from django.contrib.auth import logout

GIRIS_ZAMANI = "panel_giris_zamani"
SON_ETKINLIK = "panel_son_etkinlik"
OTURUM_DOLDU = "panel_oturum_doldu"


class OturumSuresiMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            simdi = int(time.time())
            giris = request.session.get(GIRIS_ZAMANI)
            son = request.session.get(SON_ETKINLIK, giris)
            if giris is None:
                request.session[GIRIS_ZAMANI] = request.session[SON_ETKINLIK] = simdi
            elif simdi - giris > settings.PANEL_OTURUM_EN_UZUN or simdi - son > settings.PANEL_HAREKETSIZLIK:
                logout(request)
                request.session[OTURUM_DOLDU] = True
            elif simdi - son >= 60:  # her istekte oturumu yeniden yazmamak için dakikada bir
                request.session[SON_ETKINLIK] = simdi
        return self.get_response(request)
