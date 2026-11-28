from django.contrib import admin
from django.urls import include, path
from django_otp.admin import OTPAdminSite

from . import api

# Django Admin'e de yalnızca 2FA doğrulanmış oturumla girilir (PANEL.md §9).
admin.site.__class__ = OTPAdminSite

urlpatterns = [
    # Django Admin yalnızca teknik sorumlular içindir; canlıda VPN arkasında tutulur (PANEL.md §3).
    path("admin/", admin.site.urls),
    path("api/saglik/", api.saglik, name="saglik"),
    path("", include("apps.panel.urls")),
]
