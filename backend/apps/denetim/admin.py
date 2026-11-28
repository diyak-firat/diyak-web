from django.contrib import admin

from .models import IslemKaydi


@admin.register(IslemKaydi)
class IslemKaydiAdmin(admin.ModelAdmin):
    """Salt okunur: işlem kayıtları eklenmez, değiştirilmez, elle silinmez."""

    list_display = ["zaman", "eylem", "kullanici", "nesne_turu", "nesne_id"]
    list_filter = ["eylem"]
    date_hierarchy = "zaman"
    readonly_fields = ["zaman", "eylem", "kullanici", "nesne_turu", "nesne_id", "ayrinti"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
