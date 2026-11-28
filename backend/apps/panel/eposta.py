"""Panelin gönderdiği e-postalar. İçerikte yalnızca gerekli bilgi bulunur."""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse


def davet_baglantisi(token: str) -> str:
    return settings.PANEL_ADRESI + reverse("panel:davet", args=[token])


def davet_epostasi_gonder(davet, token: str) -> None:
    metin = render_to_string(
        "panel/eposta/davet.txt",
        {"davet": davet, "baglanti": davet_baglantisi(token), "son_gecerlilik": davet.son_gecerlilik},
    )
    send_mail("DİYAK Panel daveti", metin, None, [davet.eposta])
