"""İlk Başkan (veya ilk Teknik sorumlu) için davet açar (PANEL.md §3, "İlk kurulum").

Şifreyi teknik sorumlu belirlemez: davet edilen kişi bağlantıyı açıp kendi şifresini ve
2FA'sını kurar. Sonraki tüm hesaplar panelden davetle açılır.

    python manage.py ilk_yonetici baskan@firat.edu.tr --bitis 2027-10-31
    python manage.py ilk_yonetici teknik@firat.edu.tr --bitis 2027-10-31 --teknik
"""

from datetime import date

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.servisler import ilk_davet_olustur
from apps.panel.eposta import davet_baglantisi, davet_epostasi_gonder


def _tarih(deger: str) -> date:
    try:
        return date.fromisoformat(deger)
    except ValueError as hata:
        raise CommandError("Tarih YYYY-AA-GG biçiminde olmalı, ör. 2027-10-31.") from hata


class Command(BaseCommand):
    help = "İlk Başkan veya ilk Teknik sorumlu için 48 saat geçerli davet oluşturur."

    def add_arguments(self, parser):
        parser.add_argument("eposta")
        parser.add_argument("--bitis", required=True, type=_tarih, help="Rolün bitişi (dönem sonu), YYYY-AA-GG")
        parser.add_argument("--teknik", action="store_true", help="Başkan yerine Teknik sorumlu daveti")
        parser.add_argument("--eposta-gonderme", action="store_true", help="Bağlantıyı yalnızca ekrana yaz")

    def handle(self, eposta, bitis, teknik, eposta_gonderme, **_):
        try:
            davet, token = ilk_davet_olustur(eposta, bitis, teknik=teknik)
        except ValidationError as hata:
            raise CommandError(" ".join(hata.messages)) from hata
        if not eposta_gonderme:
            davet_epostasi_gonder(davet, token)
            self.stdout.write(f"Davet e-postası gönderildi: {davet.eposta}")
        self.stdout.write(f"{davet.get_rol_display()} daveti oluşturuldu. Bağlantı (48 saat, tek kullanımlık):")
        self.stdout.write(davet_baglantisi(token))
