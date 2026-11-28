"""İşlem kaydı: kim, neyi, ne zaman yaptı (PANEL.md §6, §9).

Kayıtlar değiştirilmez ve elle silinmez; 1 yıldan eskiler gece görevinde silinir.
``ayrinti`` alanına kişisel veri (e-posta, ad, IP, form yanıtı) yazılmaz; kişiler ve nesneler
kimlikleriyle anılır.
"""

from django.conf import settings
from django.db import models


class Eylem(models.TextChoices):
    GIRIS = "giris", "Giriş"
    BASARISIZ_GIRIS = "basarisiz_giris", "Başarısız giriş"
    YENI_CIHAZ_GIRISI = "yeni_cihaz_girisi", "Yeni cihazdan giriş"
    DAVET = "davet", "Davet"
    DAVET_KABUL = "davet_kabul", "Davet kabulü"
    ROL_ATAMA = "rol_atama", "Rol atama"
    ROL_KALDIRMA = "rol_kaldirma", "Rol kaldırma"
    IKI_ADIM_SIFIRLAMA = "iki_adim_sifirlama", "2FA sıfırlama"
    KILIT_ACMA = "kilit_acma", "Hesap kilidini açma"
    HESAP_KAPATMA = "hesap_kapatma", "Hesap kapatma"
    SIFRE_DEGISTIRME = "sifre_degistirme", "Şifre değiştirme"
    ONAYA_GONDERME = "onaya_gonderme", "Onaya gönderme"
    ONAYLAMA = "onaylama", "Onaylama"
    DUZELTME_ISTEME = "duzeltme_isteme", "Düzeltme isteme"
    YAYIMLAMA = "yayimlama", "Yayımlama"
    YAYINDAN_KALDIRMA = "yayindan_kaldirma", "Yayından kaldırma"
    FORM_ACMA = "form_acma", "Form açma"
    FORM_KAPAMA = "form_kapama", "Form kapama"
    YANIT_GORUNTULEME = "yanit_goruntuleme", "Yanıtları görüntüleme"
    CSV_INDIRME = "csv_indirme", "CSV indirme"
    YANIT_SILME = "yanit_silme", "Yanıt silme"


class IslemKaydi(models.Model):
    kullanici = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="kullanıcı",
        help_text="Boşsa işlem sistem veya yönetim komutu tarafından yapılmıştır.",
    )
    eylem = models.CharField("eylem", max_length=40, choices=Eylem.choices)
    nesne_turu = models.CharField("nesne türü", max_length=60, blank=True)
    nesne_id = models.CharField("nesne kimliği", max_length=64, blank=True)
    zaman = models.DateTimeField("zaman", auto_now_add=True, db_index=True)
    ayrinti = models.JSONField("ayrıntı", default=dict, blank=True)

    class Meta:
        verbose_name = "işlem kaydı"
        verbose_name_plural = "işlem kayıtları"
        ordering = ["-zaman", "-id"]
        indexes = [models.Index(fields=["eylem", "-zaman"], name="denetim_eylem_zaman")]

    def __str__(self) -> str:
        return f"{self.zaman:%d.%m.%Y %H:%M} · {self.get_eylem_display()}"
