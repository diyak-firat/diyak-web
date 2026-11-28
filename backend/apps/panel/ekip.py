"""Ekip ekranı (PANEL.md §5, §8). Kurallar apps.ekip.servisler ve apps.onay.akis'tedir.

Editör ve Yönetim Kurulu düzenler, Danışman yalnızca görür, onayı Yönetim Kurulu verir. Yapılan
düzenlemeler onaya gönderilip onaylanana kadar sitede görünmez.
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts import yetki
from apps.ekip import servisler
from apps.ekip.models import BAGLANTI_TURLERI, Degisiklik, DegisiklikDurumu, Donem, Grup, Kisi
from apps.onay import akis

from .erisim import panel_gerekli
from .eposta import duzeltme_epostasi_gonder, onay_epostasi_gonder
from .forms import DonemFormu, DuzeltmeFormu, EkipOnayFormu, GrupFormu, KisiFormu

goruntuleyen = panel_gerekli(yetki.icerigi_gorebilir_mi)
hazirlayan = panel_gerekli(yetki.icerik_hazirlayabilir_mi)
onaylayan = panel_gerekli(yetki.onaylayabilir_mi)


def _hatalar(request, hata: ValidationError) -> None:
    for m in hata.messages:
        messages.error(request, m)


def _onizleme_verisi(veri: dict) -> dict:
    """Donmuş veriyi şablon için hazırlar: bağlantılar sitedeki adları ve sırasıyla."""
    gruplar = []
    for g in veri.get("gruplar", []):
        kisiler = [
            {**k, "baglanti_listesi": [(ad, k["baglantilar"][t]) for t, ad in BAGLANTI_TURLERI.items() if t in k["baglantilar"]]}
            for k in g["kisiler"]
        ]
        gruplar.append({**g, "kisiler": kisiler})
    return {"donem": veri.get("donem"), "gruplar": gruplar}


@goruntuleyen
def ana(request):
    donem = servisler.aktif_donem()
    acik = servisler.acik_degisiklik()
    return render(
        request,
        "panel/ekip/ana.html",
        {
            "donem": donem,
            "gruplar": donem.gruplar.prefetch_related("kisiler") if donem else [],
            "duzenleyebilir": yetki.icerik_hazirlayabilir_mi(request.user),
            "yayindaki": servisler.yayindaki(),
            "acik": acik,
            "onay_formu": EkipOnayFormu(initial={"ozet": acik.ozet if acik else ""}),
            "onaysiz_sayisi": Kisi.objects.filter(grup__donem=donem, yayin_onayi_tarihi__isnull=True).count()
            if donem
            else 0,
        },
    )


@goruntuleyen
def onizleme(request):
    donem = servisler.aktif_donem()
    if donem is None:
        return redirect("panel:ekip")
    return render(
        request,
        "panel/ekip/onizleme.html",
        {"veri": _onizleme_verisi(servisler.anlik_goruntu(donem)), "baslik": "Önizleme: onaya gönderilirse sitede görünecek hal"},
    )


@hazirlayan
def donem_yeni(request):
    onceki = servisler.aktif_donem()
    form = DonemFormu(request.POST or None, initial={"baslangic_icerigi": "kopyala" if onceki else "varsayilan"})
    if onceki is None:
        form.fields["baslangic_icerigi"].choices = form.fields["baslangic_icerigi"].choices[1:]
    if request.method == "POST" and form.is_valid():
        v = form.cleaned_data
        try:
            servisler.donem_olustur(
                request.user, v["ad"], v["baslangic"], v["bitis"],
                kopyalanacak=onceki if v["baslangic_icerigi"] == "kopyala" else None,
                varsayilan_gruplar=v["baslangic_icerigi"] == "varsayilan",
            )
        except ValidationError as hata:
            form.add_error(None, hata)
        else:
            messages.success(request, "Yeni dönem açıldı. Sitedeki ekip sayfası, değişiklik onaylanana kadar eski haliyle kalır.")
            return redirect("panel:ekip")
    return render(request, "panel/ekip/form.html", {"form": form, "baslik": "Yeni dönem", "dugme": "Dönemi aç"})


def _aktif_donem_veya_404():
    donem = servisler.aktif_donem()
    if donem is None:
        raise PermissionDenied
    return donem


@hazirlayan
def grup_yeni(request):
    donem = _aktif_donem_veya_404()
    form = GrupFormu(request.POST or None, initial={"tur": "birim"})
    if request.method == "POST" and form.is_valid():
        servisler.grup_kaydet(request.user, donem, form.cleaned_data["ad"], form.cleaned_data["tur"])
        messages.success(request, "Grup eklendi.")
        return redirect("panel:ekip")
    return render(request, "panel/ekip/form.html", {"form": form, "baslik": "Grup ekle", "dugme": "Grubu ekle"})


def _grup(pk):
    return get_object_or_404(Grup, pk=pk, donem__aktif=True)


def _kisi(pk):
    return get_object_or_404(Kisi.objects.select_related("grup"), pk=pk, grup__donem__aktif=True)


@hazirlayan
def grup_duzenle(request, pk: int):
    grup = _grup(pk)
    form = GrupFormu(request.POST or None, initial={"ad": grup.ad, "tur": grup.tur})
    if request.method == "POST" and form.is_valid():
        servisler.grup_kaydet(request.user, grup.donem, form.cleaned_data["ad"], form.cleaned_data["tur"], grup)
        messages.success(request, "Grup kaydedildi.")
        return redirect("panel:ekip")
    return render(
        request, "panel/ekip/form.html",
        {"form": form, "baslik": f"Grubu düzenle: {grup.ad}", "dugme": "Kaydet",
         "sil_adresi": "panel:ekip_grup_sil", "nesne": grup},
    )


@hazirlayan
def kisi_yeni(request, grup_pk: int):
    grup = _grup(grup_pk)
    return _kisi_formu(request, grup, None)


@hazirlayan
def kisi_duzenle(request, pk: int):
    kisi = _kisi(pk)
    return _kisi_formu(request, kisi.grup, kisi)


def _kisi_formu(request, grup, kisi):
    baslangic = {}
    if kisi is not None:
        baslangic = {
            "ad": kisi.ad, "gorev": kisi.gorev, "birim": kisi.birim, "eposta": kisi.eposta,
            "yayin_onayi": kisi.yayin_onayi_tarihi is not None,
            **{f"baglanti_{t}": u for t, u in kisi.baglantilar.items()},
        }
    form = KisiFormu(request.POST or None, request.FILES or None, initial=baslangic)
    if request.method == "POST" and form.is_valid():
        try:
            kisi = servisler.kisi_kaydet(
                request.user, grup, form.kisi_verisi(kisi.yayin_onayi_tarihi if kisi else None), kisi,
                foto=form.cleaned_data["foto"], foto_kaldir=form.cleaned_data["foto_kaldir"],
            )
        except ValidationError as hata:
            if hasattr(hata, "error_dict"):
                for alan, h in hata.message_dict.items():
                    form.add_error(alan if alan in form.fields else None, h)
            else:
                form.add_error("foto", hata)
        else:
            messages.success(request, f"{kisi.ad} kaydedildi.")
            return redirect("panel:ekip")
    return render(request, "panel/ekip/kisi.html", {"form": form, "kisi": kisi, "grup": grup})


def _sil(request, nesne, metin):
    if request.method == "POST":
        servisler.sil(request.user, nesne)
        messages.success(request, "Silindi. Sitedeki hal, değişiklik onaylanana kadar aynı kalır.")
        return redirect("panel:ekip")
    return render(
        request, "panel/onay_adimi.html",
        {"baslik": f"Sil: {nesne}", "metin": metin, "dugme": "Sil", "geri": "panel:ekip"},
    )


@hazirlayan
def grup_sil(request, pk: int):
    grup = _grup(pk)
    return _sil(request, grup, f"“{grup.ad}” grubu ve içindeki {grup.kisiler.count()} kişi çalışma kopyasından silinecek.")


@hazirlayan
def kisi_sil(request, pk: int):
    kisi = _kisi(pk)
    return _sil(request, kisi, f"{kisi.ad} ekip listesinden silinecek.")


@require_POST
@hazirlayan
def tasi(request, tur: str, pk: int):
    if tur not in ("grup", "kisi"):
        raise Http404
    nesne = _grup(pk) if tur == "grup" else _kisi(pk)
    servisler.tasi(request.user, nesne, -1 if request.POST.get("yon") == "yukari" else 1)
    return redirect("panel:ekip")


@require_POST
@hazirlayan
def onaya_gonder(request):
    donem = _aktif_donem_veya_404()
    form = EkipOnayFormu(request.POST)
    if not form.is_valid():
        messages.error(request, "Değişikliği bir cümleyle özetleyin.")
        return redirect("panel:ekip")
    try:
        degisiklik = servisler.onaya_gonder(request.user, donem, form.cleaned_data["ozet"])
    except ValidationError as hata:
        _hatalar(request, hata)
        return redirect("panel:ekip")
    onay_epostasi_gonder(degisiklik, gonderen=request.user, tur="ekip değişikliği",
                         adres_adi="panel:ekip_degisiklik", baslik=degisiklik.ozet)
    messages.success(request, "Ekip değişikliği Yönetim Kurulu onayına gönderildi.")
    return redirect("panel:ekip_degisiklik", pk=degisiklik.pk)


@goruntuleyen
def degisiklik(request, pk: int):
    d = get_object_or_404(Degisiklik.objects.select_related("olusturan", "onaylayan", "donem"), pk=pk)
    yayindaki = servisler.yayindaki()
    karsilastirma = None if d.durum in (DegisiklikDurumu.YAYINDA, DegisiklikDurumu.ESKI) else servisler.fark(
        yayindaki.veri if yayindaki else None, d.veri
    )
    k = request.user
    return render(
        request,
        "panel/ekip/degisiklik.html",
        {
            "d": d,
            "veri": _onizleme_verisi(d.veri),
            "fark": karsilastirma,
            "onaylayabilir": d.durum == DegisiklikDurumu.ONAY_BEKLIYOR and yetki.onaylayabilir_mi(k),
            "geri_cekebilir": d.durum == DegisiklikDurumu.ONAY_BEKLIYOR
            and (yetki.onaylayabilir_mi(k) or (d.olusturan_id == k.pk and yetki.icerik_hazirlayabilir_mi(k))),
            "duzeltme_formu": DuzeltmeFormu(),
        },
    )


@require_POST
@onaylayan
def degisiklik_onayla(request, pk: int):
    d = get_object_or_404(Degisiklik, pk=pk)
    try:
        akis.onayla(request.user, d)
        messages.success(request, "Ekip sayfası onaylandı ve yayımlandı.")
    except ValidationError as hata:
        _hatalar(request, hata)
    return redirect("panel:ekip_degisiklik", pk=pk)


@require_POST
@onaylayan
def degisiklik_duzeltme(request, pk: int):
    d = get_object_or_404(Degisiklik, pk=pk)
    form = DuzeltmeFormu(request.POST)
    if not form.is_valid():
        messages.error(request, "Neyin düzeltilmesi gerektiğini yazın.")
        return redirect("panel:ekip_degisiklik", pk=pk)
    try:
        d = akis.duzeltme_iste(request.user, d, form.cleaned_data["not_"])
        duzeltme_epostasi_gonder(d, tur="ekip değişikliği", adres_adi="panel:ekip", baslik=d.ozet, adres_arg=False)
        messages.success(request, "Değişiklik düzeltme notuyla geri gönderildi.")
    except ValidationError as hata:
        _hatalar(request, hata)
    return redirect("panel:ekip_degisiklik", pk=pk)


@require_POST
@goruntuleyen
def degisiklik_geri_cek(request, pk: int):
    d = get_object_or_404(Degisiklik, pk=pk)
    try:
        akis.geri_cek(request.user, d)
        messages.success(request, "Değişiklik geri çekildi. Düzenleyip yeniden onaya gönderebilirsiniz.")
    except ValidationError as hata:
        _hatalar(request, hata)
    return redirect("panel:ekip")
