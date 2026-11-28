"""İşlem kaydı ekranı (PANEL.md §5): Yönetim Kurulu, Danışman ve Teknik sorumlu görür; salt okunur."""

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.http import require_safe

from apps.accounts.yetki import islem_kaydini_gorebilir_mi
from apps.denetim.models import Eylem, IslemKaydi

from .erisim import panel_gerekli

SAYFA_BOYU = 50


@require_safe
@panel_gerekli(islem_kaydini_gorebilir_mi)
def liste(request):
    kayitlar = IslemKaydi.objects.select_related("kullanici")
    eylem = request.GET.get("eylem", "")
    if eylem in Eylem.values:
        kayitlar = kayitlar.filter(eylem=eylem)
    else:
        eylem = ""
    kisi = request.GET.get("kisi", "")
    if kisi.isdigit():
        kayitlar = kayitlar.filter(kullanici_id=int(kisi))
    else:
        kisi = ""
    sayfa = Paginator(kayitlar, SAYFA_BOYU).get_page(request.GET.get("sayfa"))
    kisiler = get_user_model().objects.order_by("first_name", "last_name", "email")
    return render(
        request,
        "panel/islem_kaydi.html",
        {
            "sayfa": sayfa,
            "eylemler": Eylem.choices,
            "kisiler": kisiler,
            "secili_eylem": eylem,
            "secili_kisi": kisi,
        },
    )
