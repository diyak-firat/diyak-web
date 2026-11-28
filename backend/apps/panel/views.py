"""Giriş, 2FA ve davet kabul ekranları (PANEL.md §3, §9)."""

from base64 import b32encode

import segno
from django.contrib.auth import login, logout
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST
from django_otp import login as otp_login
from django_otp import match_token
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts import servisler
from apps.accounts.yetki import panel_kullanicisi_mi
from apps.denetim.kayit import kaydet
from apps.denetim.models import Eylem

from .cihaz import cihazi_tani
from .erisim import ikinci_adim_adresi, onayli_cihazi_var, panel_gerekli
from .forms import DavetKabulFormu, GirisFormu, KodFormu
from .middleware import OTURUM_DOLDU

SONRAKI = "panel_sonraki"
DAVET = "panel_davet"


def _sonraki_adres(request) -> str:
    adres = request.session.pop(SONRAKI, "")
    if adres and url_has_allowed_host_and_scheme(adres, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return adres
    if panel_kullanicisi_mi(request.user):
        return reverse("panel:ana")
    if request.user.is_staff:
        return reverse("admin:index")
    return reverse("panel:ana")


@never_cache
@sensitive_post_parameters("password")
def giris(request):
    if request.user.is_authenticated:
        if request.user.is_verified():
            return redirect(_sonraki_adres(request))
        return redirect(ikinci_adim_adresi(request.user))
    oturum_doldu = request.session.pop(OTURUM_DOLDU, False)
    form = GirisFormu(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        sonraki = request.GET.get("next", "")
        login(request, form.get_user())
        request.session[SONRAKI] = sonraki
        return redirect(ikinci_adim_adresi(request.user))
    return render(request, "panel/giris.html", {"form": form, "oturum_doldu": oturum_doldu})


def _sifre_asamasi_gecilmis(request):
    """2FA ekranları yalnızca şifre adımını geçmiş ama henüz doğrulanmamış oturuma açılır."""
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    if request.user.is_verified():
        return redirect(_sonraki_adres(request))
    return None


@never_cache
def iki_adim(request):
    if (yonlendir := _sifre_asamasi_gecilmis(request)) is not None:
        return yonlendir
    if not onayli_cihazi_var(request.user):
        return redirect("panel:kurulum")
    form = KodFormu(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cihaz = match_token(request.user, form.cleaned_data["kod"])
        if cihaz is not None:
            otp_login(request, cihaz)
            kaydet(Eylem.GIRIS, kullanici=request.user)
            yanit = redirect(_sonraki_adres(request))
            cihazi_tani(request, yanit, request.user)
            return yanit
        kaydet(Eylem.BASARISIZ_GIRIS, kullanici=request.user, ayrinti={"asama": "iki_adim"})
        form.add_error("kod", "Kod hatalı veya süresi geçmiş. Uygulamadaki güncel kodu girin.")
    return render(request, "panel/iki_adim.html", {"form": form})


@never_cache
def kurulum(request):
    """İlk girişte TOTP kurulumu. Onaylı cihazı olan kullanıcı buraya giremez."""
    if (yonlendir := _sifre_asamasi_gecilmis(request)) is not None:
        return yonlendir
    if onayli_cihazi_var(request.user):
        return redirect("panel:iki_adim")
    cihaz = TOTPDevice.objects.filter(user=request.user, confirmed=False).first()
    if cihaz is None:
        cihaz = TOTPDevice.objects.create(user=request.user, name="Telefon", confirmed=False)
    form = KodFormu(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if cihaz.verify_token(form.cleaned_data["kod"]):
            cihaz.confirmed = True
            cihaz.save(update_fields=["confirmed"])
            otp_login(request, cihaz)
            kaydet(Eylem.GIRIS, kullanici=request.user, ayrinti={"ilk_kurulum": True})
            yanit = redirect(_sonraki_adres(request))
            cihazi_tani(request, yanit, request.user, uyar=False)
            return yanit
        form.add_error("kod", "Kod doğrulanamadı. Uygulamaya eklediğiniz hesabın güncel kodunu girin.")
    return render(
        request,
        "panel/kurulum.html",
        {
            "form": form,
            "karekod": segno.make(cihaz.config_url, error="m").png_data_uri(scale=5, border=2),
            "anahtar": b32encode(cihaz.bin_key).decode("ascii").rstrip("="),
        },
    )


@require_POST
def cikis(request):
    logout(request)
    return redirect("panel:giris")


@never_cache
def davet(request, token: str):
    """Bağlantıdaki belirteç oturuma alınır ve adres çubuğundan silinir (Referer ile sızmasın)."""
    if servisler.davet_bul(token) is None:
        return render(request, "panel/davet_gecersiz.html", status=404)
    if request.user.is_authenticated:
        logout(request)
    request.session[DAVET] = token
    return redirect("panel:davet_kabul")


@never_cache
@sensitive_post_parameters("sifre1", "sifre2")
def davet_kabul(request):
    token = request.session.get(DAVET, "")
    davet_kaydi = servisler.davet_bul(token)
    if davet_kaydi is None:
        request.session.pop(DAVET, None)
        return render(request, "panel/davet_gecersiz.html", status=404)
    form = DavetKabulFormu(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            kullanici = servisler.daveti_kullan(
                token, form.cleaned_data["sifre1"], form.cleaned_data["ad"], form.cleaned_data["soyad"]
            )
        except ValidationError as hata:
            form.add_error("sifre1", hata)
        else:
            request.session.pop(DAVET, None)
            login(request, kullanici, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("panel:kurulum")
    return render(request, "panel/davet_kabul.html", {"form": form, "davet": davet_kaydi})


@panel_gerekli()
def ana(request):
    from apps.accounts.models import RolAtamasi

    from apps.accounts.yetki import icerik_hazirlayabilir_mi, onaylayabilir_mi
    from apps.duyurular.models import Durum, Duyuru
    from apps.ekip.models import Degisiklik, DegisiklikDurumu

    k = request.user
    rollerim = RolAtamasi.objects.etkin().filter(kullanici=k).order_by("rol")
    onay_bekleyenler = Duyuru.objects.filter(durum=Durum.ONAY_BEKLIYOR).order_by("guncelleme") if onaylayabilir_mi(k) else None
    ekip_bekleyen = (
        Degisiklik.objects.filter(durum=DegisiklikDurumu.ONAY_BEKLIYOR).select_related("olusturan").first()
        if onaylayabilir_mi(k)
        else None
    )
    taslaklarim = (
        Duyuru.objects.filter(olusturan=k, durum__in=[Durum.TASLAK, Durum.ONAY_BEKLIYOR]).order_by("-guncelleme")
        if icerik_hazirlayabilir_mi(k)
        else None
    )
    return render(
        request,
        "panel/ana.html",
        {"rollerim": rollerim, "onay_bekleyenler": onay_bekleyenler, "ekip_bekleyen": ekip_bekleyen, "taslaklarim": taslaklarim},
    )
