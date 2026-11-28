"""Hesabım ekranı (PANEL.md §5): şifre değiştirme, 2FA cihazı, son girişler."""

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.debug import sensitive_post_parameters
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import RolAtamasi
from apps.denetim.kayit import kaydet
from apps.denetim.models import Eylem, IslemKaydi

from .erisim import panel_gerekli
from .forms import SifreDegistirmeFormu

GIRIS_EYLEMLERI = [Eylem.GIRIS, Eylem.BASARISIZ_GIRIS, Eylem.YENI_CIHAZ_GIRISI, Eylem.SIFRE_DEGISTIRME]


@panel_gerekli()
def hesabim(request):
    k = request.user
    return render(
        request,
        "panel/hesabim/hesabim.html",
        {
            "roller": RolAtamasi.objects.etkin().filter(kullanici=k).order_by("rol"),
            "cihazlar": TOTPDevice.objects.filter(user=k, confirmed=True).order_by("created_at"),
            "olaylar": IslemKaydi.objects.filter(kullanici=k, eylem__in=GIRIS_EYLEMLERI)[:15],
        },
    )


@panel_gerekli()
@sensitive_post_parameters("old_password", "new_password1", "new_password2")
def sifre_degistir(request):
    form = SifreDegistirmeFormu(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        kullanici = form.save()
        update_session_auth_hash(request, kullanici)  # bu oturum açık kalır, diğer oturumlar düşer
        kaydet(Eylem.SIFRE_DEGISTIRME, kullanici=kullanici)
        metin = render_to_string("panel/eposta/sifre_degisti.txt", {"zaman": timezone.localtime()})
        send_mail("DİYAK Panel: şifreniz değiştirildi", metin, None, [kullanici.email])
        messages.success(request, "Şifreniz değiştirildi. Diğer cihazlardaki oturumlarınız kapandı.")
        return redirect("panel:hesabim")
    return render(request, "panel/hesabim/sifre.html", {"form": form})
