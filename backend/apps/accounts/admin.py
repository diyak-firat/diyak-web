from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import KullaniciDegistirmeFormu, KullaniciOlusturmaFormu
from .models import Davet, Kullanici, RolAtamasi


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


class SaltOkunurAdmin(admin.ModelAdmin):
    """Roller ve davetler yalnızca panelden, yetki kurallarıyla ve işlem kaydıyla değişir
    (PANEL.md §4). Admin'de yalnızca görüntülenir; ilk Başkan `manage.py ilk_yonetici` ile açılır.
    """

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RolAtamasi)
class RolAtamasiAdmin(SaltOkunurAdmin):
    list_display = ["kullanici", "rol", "gorev_adi", "baslangic", "bitis", "atayan"]
    list_filter = ["rol"]
    search_fields = ["kullanici__email"]


@admin.register(Davet)
class DavetAdmin(SaltOkunurAdmin):
    list_display = ["eposta", "rol", "gorev_adi", "olusturma", "kullanildi", "davet_eden"]
    list_filter = ["rol"]
    exclude = ["token_ozeti"]
