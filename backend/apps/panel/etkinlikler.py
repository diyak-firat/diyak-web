"""Etkinlikler ekranı (PANEL.md §5). Kurallar apps.etkinlikler.servisler'dedir.

Etkinliğin kendisi sitede tek başına yayımlanmaz; bir duyuruya (ve A4'te kayıt formuna) bağlanır.
Yayındaki bir duyuruya bağlı etkinliği yalnızca Yönetim Kurulu değiştirir.
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts import yetki
from apps.etkinlikler import servisler
from apps.etkinlikler.models import Etkinlik

from .erisim import panel_gerekli
from .forms import EtkinlikFormu

goruntuleyen = panel_gerekli(yetki.icerigi_gorebilir_mi)
hazirlayan = panel_gerekli(yetki.icerik_hazirlayabilir_mi)


@goruntuleyen
def liste(request):
    simdi = timezone.now()
    tum = Etkinlik.objects.prefetch_related("duyurular")
    return render(
        request,
        "panel/etkinlikler/liste.html",
        {
            "yaklasan": tum.filter(baslangic__gte=simdi).order_by("baslangic"),
            "gecmis": tum.filter(baslangic__lt=simdi).order_by("-baslangic")[:50],
            "yeni_ekleyebilir": yetki.icerik_hazirlayabilir_mi(request.user),
        },
    )


def _baslangic(e: Etkinlik) -> dict:
    return {
        "ad": e.ad, "aciklama": e.aciklama, "baslangic": timezone.localtime(e.baslangic),
        "bitis": timezone.localtime(e.bitis) if e.bitis else None, "yer": e.yer,
        "harita_baglantisi": e.harita_baglantisi, "cevrim_ici": e.cevrim_ici,
    }


def _kaydet(request, form, etkinlik):
    try:
        etkinlik = servisler.kaydet_etkinlik(request.user, form.cleaned_data, etkinlik)
    except ValidationError as hata:
        for alan, hatalar in hata.message_dict.items():
            form.add_error(alan if alan in form.fields else None, hatalar)
        return None
    messages.success(request, "Etkinlik kaydedildi.")
    return redirect("panel:etkinlik", pk=etkinlik.pk)


@hazirlayan
def yeni(request):
    form = EtkinlikFormu(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if (yanit := _kaydet(request, form, None)) is not None:
            return yanit
    return render(request, "panel/etkinlikler/duzenle.html", {"form": form, "etkinlik": None})


@goruntuleyen
def detay(request, pk: int):
    etkinlik = get_object_or_404(Etkinlik.objects.prefetch_related("duyurular"), pk=pk)
    duzenleyebilir = servisler.duzenleyebilir_mi(request.user, etkinlik)
    if request.method == "POST" and not duzenleyebilir:
        raise PermissionDenied
    form = EtkinlikFormu(request.POST or None, initial=_baslangic(etkinlik)) if duzenleyebilir else None
    if request.method == "POST" and form.is_valid():
        if (yanit := _kaydet(request, form, etkinlik)) is not None:
            return yanit
    return render(
        request,
        "panel/etkinlikler/duzenle.html",
        {
            "form": form,
            "etkinlik": etkinlik,
            "yayina_bagli": servisler._yayina_bagli(etkinlik),
            "silinebilir": servisler.silinebilir_mi(etkinlik) and yetki.icerik_hazirlayabilir_mi(request.user),
        },
    )


@hazirlayan
def sil(request, pk: int):
    etkinlik = get_object_or_404(Etkinlik, pk=pk)
    if not servisler.silinebilir_mi(etkinlik):
        raise PermissionDenied
    if request.method == "POST":
        servisler.sil(request.user, etkinlik)
        messages.success(request, "Etkinlik silindi.")
        return redirect("panel:etkinlikler")
    return render(
        request, "panel/onay_adimi.html",
        {"baslik": f"Sil: {etkinlik.ad}", "metin": "Etkinlik kalıcı olarak silinecek.", "dugme": "Etkinliği sil",
         "geri": "panel:etkinlikler"},
    )
