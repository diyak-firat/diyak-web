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


def onay_epostasi_gonder(nesne, gonderen=None, tur="duyuru", adres_adi="panel:duyuru", baslik=None) -> None:
    """Onaya gönderilen içerik için Yönetim Kurulu'na bildirim. Yalnızca başlık ve panel bağlantısı."""
    alicilar = _yk_epostalari(haric=gonderen)
    if not alicilar:
        return
    metin = render_to_string(
        "panel/eposta/onay_bekliyor.txt",
        {"tur": tur, "baslik": baslik or nesne.baslik, "baglanti": settings.PANEL_ADRESI + reverse(adres_adi, args=[nesne.pk])},
    )
    send_mail(f"DİYAK Panel: onay bekleyen 1 {tur} var", metin, None, alicilar)


def duzeltme_epostasi_gonder(nesne, tur="duyuru", adres_adi="panel:duyuru", baslik=None, adres_arg=True) -> None:
    """Düzeltme istendiğinde hazırlayana bildirim. Notun kendisi panelde görünür."""
    if nesne.olusturan is None or not nesne.olusturan.is_active:
        return
    adres = reverse(adres_adi, args=[nesne.pk]) if adres_arg else reverse(adres_adi)
    metin = render_to_string(
        "panel/eposta/duzeltme_istendi.txt",
        {"tur": tur, "baslik": baslik or nesne.baslik, "baglanti": settings.PANEL_ADRESI + adres},
    )
    send_mail(f"DİYAK Panel: {tur} için düzeltme istendi", metin, None, [nesne.olusturan.email])
