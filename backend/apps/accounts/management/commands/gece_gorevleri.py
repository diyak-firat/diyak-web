"""Her gece bir kez çalışır (sunucuda cron veya systemd zamanlayıcısıyla; OPERASYON.md).

    python manage.py gece_gorevleri

Şimdilik: rol bitiş hatırlatması ve saklama süresi dolan kayıtların silinmesi. Form kapama ve
yanıt silme görevleri A4/A5'te buraya eklenecek.
"""

from django.core.management.base import BaseCommand

from apps.accounts.bakim import eski_kayitlari_sil, rol_hatirlatmasi_gonder


class Command(BaseCommand):
    help = "Gece görevleri: rol bitiş hatırlatması ve eski kayıtların silinmesi."

    def handle(self, **_):
        eposta = rol_hatirlatmasi_gonder()
        silinen = eski_kayitlari_sil()
        ozet = ", ".join(f"{ad}={sayi}" for ad, sayi in silinen.items())
        self.stdout.write(f"rol hatırlatması: {eposta} e-posta · silinen: {ozet}")
