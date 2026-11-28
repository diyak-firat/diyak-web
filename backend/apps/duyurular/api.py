"""/api/duyurular/ (PANEL.md §11, K-23). Astro derleme sırasında okur.

Yalnızca yayımlanmış duyurular döner. Alanlar tek tek yazılır; hazırlayan, onaylayan, onay notu
gibi panel içi bilgiler API'de yoktur. Salt okunurdur, giriş gerektirmez.
"""

from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny

from apps.etkinlikler.models import Etkinlik

from .models import Durum, Duyuru


class EtkinlikSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etkinlik
        fields = ["baslangic", "bitis", "yer", "cevrim_ici"]


class DuyuruSerializer(serializers.ModelSerializer):
    # Sitedeki etiket adlarıyla aynı: "Etkinlik", "Duyuru", "Çağrı", "Yayın" (frontend/src/lib/etiketler.ts)
    etiket = serializers.CharField(source="get_etiket_display")
    etkinlik = EtkinlikSerializer(allow_null=True)

    class Meta:
        model = Duyuru
        fields = ["slug", "baslik", "etiket", "ozet", "govde", "yayin_tarihi", "etkinlik"]


def _yayimlananlar():
    return Duyuru.objects.filter(durum=Durum.YAYINDA).select_related("etkinlik").order_by("-yayin_tarihi", "-pk")


class DuyuruListesi(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = DuyuruSerializer
    pagination_class = None

    def get_queryset(self):
        return _yayimlananlar()


class DuyuruAyrintisi(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = DuyuruSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return _yayimlananlar()
