"""/api/ekip/ (PANEL.md §11): en son onaylanan ekip sayfası. Yalnızca yayın onayı olan kişiler ve
herkese açık alanlar döner (bkz. servisler.anlik_goruntu). Salt okunur, giriş gerektirmez.
"""

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import BAGLANTI_TURLERI
from .servisler import yayindaki


@api_view(["GET"])
@permission_classes([AllowAny])
def ekip(request):
    degisiklik = yayindaki()
    if degisiklik is None:
        return Response({"donem": None, "yayin_tarihi": None, "gruplar": []})
    veri = degisiklik.veri
    gruplar = [
        {
            "ad": g["ad"],
            "tur": g["tur"],
            "kisiler": [
                {
                    "ad": k["ad"],
                    "gorev": k["gorev"],
                    "birim": k["birim"],
                    "eposta": k["eposta"],
                    "foto": request.build_absolute_uri(settings.MEDIA_URL + k["foto"]) if k["foto"] else None,
                    # Sıra her kişide aynı: BAGLANTI_TURLERI sırası (jsonb anahtar sırasını korumaz).
                    "baglantilar": [
                        {"ad": ad, "url": k["baglantilar"][tur]}
                        for tur, ad in BAGLANTI_TURLERI.items()
                        if tur in k["baglantilar"]
                    ],
                }
                for k in g["kisiler"]
            ],
        }
        for g in veri.get("gruplar", [])
    ]
    return Response({"donem": veri.get("donem"), "yayin_tarihi": degisiklik.yayin_tarihi, "gruplar": gruplar})
