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


def _yk_epostalari(haric=None) -> list[str]:
    from apps.accounts.models import Rol, RolAtamasi

    sorgu = RolAtamasi.objects.etkin().filter(rol=Rol.YONETIM_KURULU)
    if haric is not None:
        sorgu = sorgu.exclude(kullanici=haric)
    return sorted(set(sorgu.values_list("kullanici__email", flat=True)))


def onay_epostasi_gonder(duyuru, gonderen=None) -> None:
    """Onaya gönderilen içerik için Yönetim Kurulu'na bildirim. Yalnızca başlık ve panel bağlantısı."""
    alicilar = _yk_epostalari(haric=gonderen)
    if not alicilar:
        return
    metin = render_to_string(
        "panel/eposta/onay_bekliyor.txt",
        {"tur": "duyuru", "baslik": duyuru.baslik, "baglanti": settings.PANEL_ADRESI + reverse("panel:duyuru", args=[duyuru.pk])},
    )
    send_mail("DİYAK Panel: onay bekleyen 1 duyuru var", metin, None, alicilar)


def duzeltme_epostasi_gonder(duyuru) -> None:
    """Düzeltme istendiğinde hazırlayana bildirim. Notun kendisi panelde görünür."""
    if duyuru.olusturan is None or not duyuru.olusturan.is_active:
        return
    metin = render_to_string(
        "panel/eposta/duzeltme_istendi.txt",
        {"tur": "duyuru", "baslik": duyuru.baslik, "baglanti": settings.PANEL_ADRESI + reverse("panel:duyuru", args=[duyuru.pk])},
    )
    send_mail("DİYAK Panel: duyurunuz için düzeltme istendi", metin, None, [duyuru.olusturan.email])
