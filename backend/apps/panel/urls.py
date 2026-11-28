from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path("", views.ana, name="ana"),
    path("giris/", views.giris, name="giris"),
    path("giris/dogrulama/", views.iki_adim, name="iki_adim"),
    path("giris/iki-adim-kurulumu/", views.kurulum, name="kurulum"),
    path("cikis/", views.cikis, name="cikis"),
    path("davet/", views.davet_kabul, name="davet_kabul"),
    path("davet/<str:token>/", views.davet, name="davet"),
]
