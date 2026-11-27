from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import KullaniciDegistirmeFormu, KullaniciOlusturmaFormu
from .models import Kullanici


@admin.register(Kullanici)
class KullaniciAdmin(UserAdmin):
    form = KullaniciDegistirmeFormu
    add_form = KullaniciOlusturmaFormu
    ordering = ["email"]
    list_display = ["email", "first_name", "last_name", "is_active", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Kişisel bilgiler", {"fields": ("first_name", "last_name")}),
        ("Yetkiler", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Tarihler", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)
