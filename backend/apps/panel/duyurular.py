"""Duyurular ekranları (PANEL.md §5, §8). Kurallar apps.duyurular.servisler ve apps.onay.akis'tedir;
burada yalnızca çağrılır. Onay işlemleri yalnızca POST ile yapılır (CSRF korumalı).
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts import yetki
from apps.duyurular import servisler
from apps.duyurular.models import Durum, Duyuru, Etiket
from apps.onay import akis

from .erisim import panel_gerekli
from .eposta import duzeltme_epostasi_gonder, onay_epostasi_gonder
from .forms import DuyuruFormu, DuzeltmeFormu

goruntuleyen = panel_gerekli(yetki.icerigi_gorebilir_mi)
hazirlayan = panel_gerekli(yetki.icerik_hazirlayabilir_mi)
onaylayan = panel_gerekli(yetki.onaylayabilir_mi)


def _hata_mesaji(request, hata: ValidationError) -> None:
    for m in hata.messages:
        messages.error(request, m)


@goruntuleyen
def liste(request):
    duyurular = Duyuru.objects.select_related("olusturan")
    durum = request.GET.get("durum", "")
    etiket = request.GET.get("etiket", "")
    if durum in Durum.values:
        duyurular = duyurular.filter(durum=durum)
    else:
        durum = ""
    if etiket in Etiket.values:
        duyurular = duyurular.filter(etiket=etiket)
    else:
        etiket = ""
    return render(
        request,
        "panel/duyurular/liste.html",
        {
            "duyurular": duyurular,
            "durumlar": Durum.choices,
            "etiketler": Etiket.choices,
            "secili_durum": durum,
            "secili_etiket": etiket,
            "yeni_yazabilir": yetki.icerik_hazirlayabilir_mi(request.user),
        },
    )


def _baslangic(duyuru: Duyuru | None) -> dict:
    if duyuru is None:
        return {"etiket": Etiket.DUYURU}
    veri = {"baslik": duyuru.baslik, "etiket": duyuru.etiket, "ozet": duyuru.ozet, "govde": duyuru.govde}
    if duyuru.etkinlik:
        veri["etkinlik_baslangic"] = timezone.localtime(duyuru.etkinlik.baslangic)
        veri["etkinlik_yer"] = duyuru.etkinlik.yer
    return veri


def _kaydet_ve_ilerle(request, form, duyuru):
    """Formu kaydeder; düğmeye göre onaya gönderir veya (YK) yayımlar. Yönlendirme döndürür."""
    islem = request.POST.get("islem", "kaydet")
    if islem == "yayimla" and not yetki.onaylayabilir_mi(request.user):
        raise PermissionDenied
    try:
        duyuru = servisler.kaydet_duyuru(request.user, form.duyuru_verisi(), duyuru, form.etkinlik_bilgisi())
    except ValidationError as hata:
        _hata_mesaji(request, hata)
        return None
    try:
        if islem in ("onaya_gonder", "yayimla") and duyuru.durum == Durum.TASLAK:
            duyuru = akis.onaya_gonder(request.user, duyuru)
            if islem == "yayimla":
                duyuru = akis.onayla(request.user, duyuru)
                messages.success(request, "Duyuru yayımlandı. Site birkaç dakika içinde güncellenir.")
            else:
                onay_epostasi_gonder(duyuru, gonderen=request.user)
                messages.success(request, "Duyuru Yönetim Kurulu onayına gönderildi.")
        else:
            messages.success(request, "Kaydedildi.")
    except ValidationError as hata:
        messages.success(request, "Taslak kaydedildi.")
        _hata_mesaji(request, hata)
    return redirect("panel:duyuru", pk=duyuru.pk)


@hazirlayan
def yeni(request):
    form = DuyuruFormu(request.POST or None, initial=_baslangic(None))
    if request.method == "POST" and form.is_valid():
        if (yanit := _kaydet_ve_ilerle(request, form, None)) is not None:
            return yanit
    return render(request, "panel/duyurular/duzenle.html", _duzenleme_baglami(request, form, None))


def _duzenleme_baglami(request, form, duyuru):
    return {
        "form": form,
        "duyuru": duyuru,
        "yk": yetki.onaylayabilir_mi(request.user),
        "simdi": timezone.now(),
    }


@goruntuleyen
def detay(request, pk: int):
    duyuru = get_object_or_404(Duyuru.objects.select_related("etkinlik", "olusturan", "onaylayan"), pk=pk)
    if servisler.duzenleyebilir_mi(request.user, duyuru):
        form = DuyuruFormu(request.POST or None, initial=_baslangic(duyuru))
        if request.method == "POST" and form.is_valid():
            if (yanit := _kaydet_ve_ilerle(request, form, duyuru)) is not None:
                return yanit
        return render(request, "panel/duyurular/duzenle.html", _duzenleme_baglami(request, form, duyuru))
    if request.method == "POST":
        raise PermissionDenied
    k = request.user
    return render(
        request,
        "panel/duyurular/goruntule.html",
        {
            "duyuru": duyuru,
            "onaylayabilir": duyuru.durum == Durum.ONAY_BEKLIYOR and yetki.onaylayabilir_mi(k),
            "geri_cekebilir": duyuru.durum == Durum.ONAY_BEKLIYOR
            and (yetki.onaylayabilir_mi(k) or (duyuru.olusturan_id == k.pk and yetki.icerik_hazirlayabilir_mi(k))),
            "duzeltme_formu": DuzeltmeFormu(),
        },
    )


@goruntuleyen
def onizleme(request, pk: int):
    duyuru = get_object_or_404(Duyuru.objects.select_related("etkinlik"), pk=pk)
    return render(request, "panel/duyurular/onizleme.html", {"duyuru": duyuru})


@require_POST
@onaylayan
def onayla(request, pk: int):
    duyuru = get_object_or_404(Duyuru, pk=pk)
    try:
        akis.onayla(request.user, duyuru)
        messages.success(request, "Onaylandı ve yayımlandı. Site birkaç dakika içinde güncellenir.")
    except ValidationError as hata:
        _hata_mesaji(request, hata)
    return redirect("panel:duyuru", pk=pk)


@require_POST
@onaylayan
def duzeltme_iste(request, pk: int):
    duyuru = get_object_or_404(Duyuru, pk=pk)
    form = DuzeltmeFormu(request.POST)
    if not form.is_valid():
        messages.error(request, "Neyin düzeltilmesi gerektiğini yazın.")
        return redirect("panel:duyuru", pk=pk)
    try:
        duyuru = akis.duzeltme_iste(request.user, duyuru, form.cleaned_data["not_"])
        duzeltme_epostasi_gonder(duyuru)
        messages.success(request, "Duyuru düzeltme notuyla hazırlayana geri gönderildi.")
    except ValidationError as hata:
        _hata_mesaji(request, hata)
    return redirect("panel:duyuru", pk=pk)


@require_POST
@hazirlayan
def onaya_gonder(request, pk: int):
    duyuru = get_object_or_404(Duyuru, pk=pk)
    try:
        duyuru = akis.onaya_gonder(request.user, duyuru)
        onay_epostasi_gonder(duyuru, gonderen=request.user)
        messages.success(request, "Duyuru Yönetim Kurulu onayına gönderildi.")
    except ValidationError as hata:
        _hata_mesaji(request, hata)
    return redirect("panel:duyuru", pk=pk)


@require_POST
@goruntuleyen
def geri_cek(request, pk: int):
    duyuru = get_object_or_404(Duyuru, pk=pk)
    try:
        akis.geri_cek(request.user, duyuru)
        messages.success(request, "Duyuru taslağa geri alındı; düzenleyebilirsiniz.")
    except ValidationError as hata:
        _hata_mesaji(request, hata)
    return redirect("panel:duyuru", pk=pk)


@onaylayan
def yayindan_kaldir(request, pk: int):
    duyuru = get_object_or_404(Duyuru, pk=pk, durum=Durum.YAYINDA)
    if request.method == "POST":
        servisler.yayindan_kaldir(request.user, duyuru)
        messages.success(request, "Duyuru yayından kaldırıldı. Site birkaç dakika içinde güncellenir.")
        return redirect("panel:duyuru", pk=pk)
    return render(
        request,
        "panel/duyurular/onay_adimi.html",
        {
            "duyuru": duyuru,
            "baslik": "Yayından kaldır",
            "metin": "Duyuru sitedeki gündemden ve RSS'ten kalkar. Daha sonra düzenleyip yeniden onaya gönderebilirsiniz.",
            "dugme": "Yayından kaldır",
        },
    )


@hazirlayan
def sil(request, pk: int):
    duyuru = get_object_or_404(Duyuru, pk=pk)
    if not (duyuru.durum == Durum.TASLAK and duyuru.yayin_tarihi is None):
        raise PermissionDenied
    if not (duyuru.olusturan_id == request.user.pk or yetki.onaylayabilir_mi(request.user)):
        raise PermissionDenied
    if request.method == "POST":
        servisler.sil(request.user, duyuru)
        messages.success(request, "Taslak silindi.")
        return redirect("panel:duyurular")
    return render(
        request,
        "panel/duyurular/onay_adimi.html",
        {
            "duyuru": duyuru,
            "baslik": "Taslağı sil",
            "metin": "Taslak kalıcı olarak silinecek. Bu işlem geri alınamaz.",
            "dugme": "Taslağı sil",
        },
    )
