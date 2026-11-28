from django.urls import path

from . import duyurular, hesabim, islem_kaydi, kullanicilar, views

app_name = "panel"

urlpatterns = [
    path("", views.ana, name="ana"),
    path("giris/", views.giris, name="giris"),
    path("giris/dogrulama/", views.iki_adim, name="iki_adim"),
    path("giris/iki-adim-kurulumu/", views.kurulum, name="kurulum"),
    path("cikis/", views.cikis, name="cikis"),
    path("davet/", views.davet_kabul, name="davet_kabul"),
    path("davet/<str:token>/", views.davet, name="davet"),
    path("duyurular/", duyurular.liste, name="duyurular"),
    path("duyurular/yeni/", duyurular.yeni, name="duyuru_yeni"),
    path("duyurular/<int:pk>/", duyurular.detay, name="duyuru"),
    path("duyurular/<int:pk>/onizleme/", duyurular.onizleme, name="duyuru_onizleme"),
    path("duyurular/<int:pk>/onaya-gonder/", duyurular.onaya_gonder, name="duyuru_onaya_gonder"),
    path("duyurular/<int:pk>/onayla/", duyurular.onayla, name="duyuru_onayla"),
    path("duyurular/<int:pk>/duzeltme-iste/", duyurular.duzeltme_iste, name="duyuru_duzeltme_iste"),
    path("duyurular/<int:pk>/geri-cek/", duyurular.geri_cek, name="duyuru_geri_cek"),
    path("duyurular/<int:pk>/yayindan-kaldir/", duyurular.yayindan_kaldir, name="duyuru_yayindan_kaldir"),
    path("duyurular/<int:pk>/sil/", duyurular.sil, name="duyuru_sil"),
    path("islem-kaydi/", islem_kaydi.liste, name="islem_kaydi"),
    path("hesabim/", hesabim.hesabim, name="hesabim"),
    path("hesabim/sifre/", hesabim.sifre_degistir, name="hesabim_sifre"),
    path("kullanicilar/", kullanicilar.liste, name="kullanicilar"),
    path("kullanicilar/davet/", kullanicilar.davet_et, name="kullanici_davet"),
    path("kullanicilar/<int:pk>/", kullanicilar.detay, name="kullanici"),
    path("kullanicilar/<int:pk>/roller/<int:atama_pk>/kaldir/", kullanicilar.rol_kaldir, name="kullanici_rol_kaldir"),
    path("kullanicilar/<int:pk>/kapat/", kullanicilar.kapat, name="kullanici_kapat"),
    path("kullanicilar/<int:pk>/iki-adim-sifirla/", kullanicilar.iki_adim_sifirla, name="kullanici_iki_adim_sifirla"),
    path("kullanicilar/<int:pk>/kilidi-ac/", kullanicilar.kilidi_ac, name="kullanici_kilidi_ac"),
]
