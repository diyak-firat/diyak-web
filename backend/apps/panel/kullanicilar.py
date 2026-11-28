"""Kullanıcılar ekranı (PANEL.md §4, §5): davet, rol atama ve kaldırma, hesabı kapatma;
teknik sorumlu için 2FA sıfırlama ve kilit açma. Yetki kuralları ``apps.accounts.yetki``'dedir;
burada yalnızca çağrılır.
"""

from datetime import timedelta

from axes.models import AccessAttempt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts import servisler, yetki
from apps.accounts.models import ATAMA_YETKILI_GOREVLER, Davet, RolAtamasi

from .eposta import davet_epostasi_gonder
from .erisim import panel_gerekli
from .forms import DavetFormu, RolAtamaFormu

YAKINDA_BITIS_GUN = 14
yonetici_gerekli = panel_gerekli(yetki.kullanicilari_yonetebilir_mi)


def _varsayilan_bitis(kullanici):
    """Varsayılan bitiş: atayanın kendi rolünün bitişi (çoğunlukla dönem sonu)."""
    atama = RolAtamasi.objects.etkin().filter(kullanici=kullanici).order_by("-bitis").first()
    return atama.bitis if atama else None


def _hata_ekle(form, hata: ValidationError) -> None:
    if hasattr(hata, "error_dict"):
        for alan, hatalar in hata.message_dict.items():
            form.add_error(alan if alan in form.fields else None, hatalar)
    else:
        form.add_error(None, hata.messages)


def _kilitli_mi(kullanici) -> bool:
    sinir = timezone.now() - settings.AXES_COOLOFF_TIME
    return AccessAttempt.objects.filter(
        username=kullanici.email.lower(), failures_since_start__gte=settings.AXES_FAILURE_LIMIT, attempt_time__gte=sinir
    ).exists()


def _ortak(request) -> dict:
    return {"gorev_onerileri": [*ATAMA_YETKILI_GOREVLER, "Sayman", "Sekreter", "Birim Sorumlusu"]}


@yonetici_gerekli
def liste(request):
    bugun = timezone.localdate()
    etkin = RolAtamasi.objects.etkin().select_related("kullanici").order_by("rol", "gorev_adi")
    kullanicilar = (
        get_user_model()
        .objects.order_by("-is_active", "first_name", "last_name", "email")
        .prefetch_related(Prefetch("rol_atamalari", queryset=RolAtamasi.objects.etkin(), to_attr="etkin_atamalar"))
    )
    davetler = [d for d in Davet.objects.filter(kullanildi__isnull=True).order_by("-olusturma") if d.gecerli_mi()]
    return render(
        request,
        "panel/kullanicilar/liste.html",
        {
            "kullanicilar": kullanicilar,
            "yakinda_bitenler": etkin.filter(bitis__lte=bugun + timedelta(days=YAKINDA_BITIS_GUN)).order_by("bitis"),
            "davetler": davetler,
            "davet_edebilir": bool(yetki.atanabilir_roller(request.user)),
        },
    )


@yonetici_gerekli
def davet_et(request):
    roller = yetki.atanabilir_roller(request.user)
    form = DavetFormu(request.POST or None, roller=roller, initial={"bitis": _varsayilan_bitis(request.user)})
    if request.method == "POST" and form.is_valid():
        v = form.cleaned_data
        try:
            davet, token = servisler.davet_olustur(request.user, v["eposta"], v["rol"], v["bitis"], v["gorev_adi"])
        except ValidationError as hata:
            _hata_ekle(form, hata)
        else:
            davet_epostasi_gonder(davet, token)
            messages.success(request, f"Davet {davet.eposta} adresine gönderildi. Bağlantı 48 saat geçerli.")
            return redirect("panel:kullanicilar")
    return render(request, "panel/kullanicilar/davet.html", {"form": form, **_ortak(request)})


def _hedef(pk: int):
    return get_object_or_404(get_user_model(), pk=pk)


@yonetici_gerekli
def detay(request, pk: int):
    hedef = _hedef(pk)
    kendisi = hedef.pk == request.user.pk
    roller = frozenset() if kendisi else yetki.atanabilir_roller(request.user)
    form = RolAtamaFormu(request.POST or None, roller=roller, initial={"bitis": _varsayilan_bitis(request.user)})
    if request.method == "POST":
        if not roller:
            raise PermissionDenied
        if form.is_valid():
            v = form.cleaned_data
            try:
                servisler.rol_ata(request.user, hedef, v["rol"], v["bitis"], v["gorev_adi"])
            except ValidationError as hata:
                _hata_ekle(form, hata)
            else:
                messages.success(request, "Rol atandı.")
                return redirect("panel:kullanici", pk=hedef.pk)
    bugun = timezone.localdate()
    atamalar = [
        {
            "atama": a,
            "durum": "etkin" if a.etkin_mi(bugun) else ("başlamadı" if a.baslangic > bugun else "bitti"),
            "kaldirabilir": a.rol in roller,
        }
        for a in hedef.rol_atamalari.select_related("atayan").order_by("-bitis")
    ]
    return render(
        request,
        "panel/kullanicilar/detay.html",
        {
            "hedef": hedef,
            "atamalar": atamalar,
            "form": form if roller else None,
            "iki_adim_kurulu": TOTPDevice.objects.filter(user=hedef, confirmed=True).exists(),
            "kilitli": _kilitli_mi(hedef),
            "teknik": yetki.teknik_mi(request.user) and hedef.pk != request.user.pk,
            "kapatabilir": yetki.hesabi_kapatabilir_mi(request.user, hedef),
            "kendisi": kendisi,
            **_ortak(request),
        },
    )


def _onay_sayfasi(request, hedef, baslik: str, metin: str, dugme: str):
    return render(request, "panel/kullanicilar/onay.html", {"hedef": hedef, "baslik": baslik, "metin": metin, "dugme": dugme})


@yonetici_gerekli
def rol_kaldir(request, pk: int, atama_pk: int):
    hedef = _hedef(pk)
    atama = get_object_or_404(RolAtamasi, pk=atama_pk, kullanici=hedef)
    if not yetki.rolunu_degistirebilir_mi(request.user, hedef, atama.rol):
        raise PermissionDenied
    if request.method == "POST":
        servisler.rol_kaldir(request.user, atama)
        messages.success(request, "Rol kaldırıldı.")
        return redirect("panel:kullanici", pk=hedef.pk)
    gorev = f" ({atama.gorev_adi})" if atama.gorev_adi else ""
    return _onay_sayfasi(
        request,
        hedef,
        "Rolü kaldır",
        f"{hedef.get_full_name() or hedef.email} kişisinin {atama.get_rol_display()}{gorev} rolü hemen sona erecek. "
        "Bu rolün verdiği yetkiler aynı anda kalkar.",
        "Rolü kaldır",
    )


@yonetici_gerekli
def kapat(request, pk: int):
    hedef = _hedef(pk)
    if not yetki.hesabi_kapatabilir_mi(request.user, hedef):
        raise PermissionDenied
    if request.method == "POST":
        servisler.hesabi_kapat(request.user, hedef)
        messages.success(request, "Hesap kapatıldı.")
        return redirect("panel:kullanici", pk=hedef.pk)
    return _onay_sayfasi(
        request,
        hedef,
        "Hesabı kapat",
        f"{hedef.get_full_name() or hedef.email} panele bir daha giremeyecek; açık oturumları hemen sona erer. "
        "Kapatılan hesap panelden yeniden açılamaz; gerekirse teknik sorumlu açar.",
        "Hesabı kapat",
    )


@yonetici_gerekli
def iki_adim_sifirla(request, pk: int):
    hedef = _hedef(pk)
    if not yetki.teknik_mi(request.user) or hedef.pk == request.user.pk:
        raise PermissionDenied
    if request.method == "POST":
        servisler.iki_adimi_sifirla(request.user, hedef)
        messages.success(request, "2FA sıfırlandı. Kişi bir sonraki girişte yeniden kuracak.")
        return redirect("panel:kullanici", pk=hedef.pk)
    return _onay_sayfasi(
        request,
        hedef,
        "2FA'yı sıfırla",
        "Kişinin doğrulama uygulaması bağlantısı silinecek. Bir sonraki girişte şifresinden sonra yeni bir "
        "karekod okutması istenecek. Bunu yalnızca kişinin kimliğinden emin olduktan sonra yapın "
        "(ör. yüz yüze veya bildiğiniz bir telefon numarasından).",
        "2FA'yı sıfırla",
    )


@require_POST
@yonetici_gerekli
def kilidi_ac(request, pk: int):
    hedef = _hedef(pk)
    if not yetki.teknik_mi(request.user):
        raise PermissionDenied
    servisler.kilidi_ac(request.user, hedef)
    messages.success(request, "Hesabın giriş kilidi açıldı.")
    return redirect("panel:kullanici", pk=hedef.pk)

