from django.urls import path

from . import kullanicilar, views

app_name = "panel"

urlpatterns = [
    path("", views.ana, name="ana"),
    path("giris/", views.giris, name="giris"),
    path("giris/dogrulama/", views.iki_adim, name="iki_adim"),
    path("giris/iki-adim-kurulumu/", views.kurulum, name="kurulum"),
    path("cikis/", views.cikis, name="cikis"),
    path("davet/", views.davet_kabul, name="davet_kabul"),
    path("davet/<str:token>/", views.davet, name="davet"),
    path("kullanicilar/", kullanicilar.liste, name="kullanicilar"),
    path("kullanicilar/davet/", kullanicilar.davet_et, name="kullanici_davet"),
    path("kullanicilar/<int:pk>/", kullanicilar.detay, name="kullanici"),
    path("kullanicilar/<int:pk>/roller/<int:atama_pk>/kaldir/", kullanicilar.rol_kaldir, name="kullanici_rol_kaldir"),
    path("kullanicilar/<int:pk>/kapat/", kullanicilar.kapat, name="kullanici_kapat"),
    path("kullanicilar/<int:pk>/iki-adim-sifirla/", kullanicilar.iki_adim_sifirla, name="kullanici_iki_adim_sifirla"),
    path("kullanicilar/<int:pk>/kilidi-ac/", kullanicilar.kilidi_ac, name="kullanici_kilidi_ac"),
]
