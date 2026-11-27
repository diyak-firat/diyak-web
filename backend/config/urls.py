from django.contrib import admin
from django.urls import path

from . import api

urlpatterns = [
    # Django Admin yalnızca teknik sorumlular içindir; canlıda VPN arkasında tutulur (PANEL.md §3).
    path("admin/", admin.site.urls),
    path("api/saglik/", api.saglik, name="saglik"),
]
