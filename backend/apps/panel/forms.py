from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm


class GirisFormu(AuthenticationForm):
    username = forms.EmailField(label="E-posta", widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "username"}))
    password = forms.CharField(
        label="Şifre", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"})
    )

    error_messages = {
        "invalid_login": "E-posta veya şifre hatalı. Büyük/küçük harfe dikkat ederek yeniden deneyin.",
        "inactive": "Bu hesap kapatılmış.",
    }


class KodFormu(forms.Form):
    kod = forms.RegexField(
        label="Doğrulama kodu",
        regex=r"^\s*\d{6}\s*$",
        error_messages={"invalid": "Kod, telefon uygulamasındaki 6 haneli sayıdır."},
        widget=forms.TextInput(
            attrs={"inputmode": "numeric", "autocomplete": "one-time-code", "autofocus": True, "maxlength": 8}
        ),
    )

    def clean_kod(self) -> str:
        return self.cleaned_data["kod"].strip()


class DavetKabulFormu(forms.Form):
    ad = forms.CharField(label="Ad", max_length=150)
    soyad = forms.CharField(label="Soyad", max_length=150)
    sifre1 = forms.CharField(
        label="Şifre",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="En az 12 karakter. Yaygın şifreler ve yalnızca rakamdan oluşan şifreler kabul edilmez.",
    )
    sifre2 = forms.CharField(
        label="Şifre (tekrar)", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )

    def clean(self):
        temiz = super().clean()
        if temiz.get("sifre1") and temiz.get("sifre1") != temiz.get("sifre2"):
            self.add_error("sifre2", "İki şifre aynı değil.")
        return temiz


class _RolAlanlari(forms.Form):
    rol = forms.ChoiceField(label="Rol")
    gorev_adi = forms.CharField(
        label="Görev adı",
        max_length=100,
        required=False,
        help_text="İsteğe bağlı, ör. İletişim Birimi. Davet ve rol atama yetkisini yalnızca Yönetim Kurulu "
        "rolündeki “Başkan” ve “Başkan Yardımcısı” görevleri verir.",
        widget=forms.TextInput(attrs={"list": "gorev-onerileri"}),
    )
    bitis = forms.DateField(
        label="Rolün bitişi",
        help_text="Bu gün dahil geçerlidir. Genellikle dönem sonu (bir sonraki Olağan Genel Kurul).",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )

    def __init__(self, *args, roller=(), **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Rol

        secenekler = [(r.value, r.label) for r in Rol if r.value in roller]
        # Birden çok seçenek varsa hiçbiri önceden seçili gelmez (yanlışlıkla Yönetim Kurulu atanmasın).
        self.fields["rol"].choices = secenekler if len(secenekler) == 1 else [("", "Seçin"), *secenekler]


class DavetFormu(_RolAlanlari):
    eposta = forms.EmailField(label="E-posta", help_text="Mümkünse üniversite e-postası.")

    field_order = ["eposta", "rol", "gorev_adi", "bitis"]


class RolAtamaFormu(_RolAlanlari):
    pass


class SifreDegistirmeFormu(PasswordChangeForm):
    error_messages = {
        **PasswordChangeForm.error_messages,
        # Bandit B105 yanlış alarm: bunlar şifre değil, hata mesajı.
        "password_incorrect": "Mevcut şifreniz hatalı. Yeniden girin.",  # nosec B105
        "password_mismatch": "İki yeni şifre aynı değil.",  # nosec B105
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "Mevcut şifre"
        self.fields["new_password1"].label = "Yeni şifre"
        self.fields["new_password1"].help_text = (
            "En az 12 karakter. Yaygın şifreler ve yalnızca rakamdan oluşan şifreler kabul edilmez."
        )
        self.fields["new_password2"].label = "Yeni şifre (tekrar)"
        self.fields["new_password2"].help_text = "Yeni şifreyi bir kez daha yazın."


class DuyuruFormu(forms.Form):
    """Duyuru düzenleme formu. Gövde editörden HTML gelir; sunucu kaydederken temizler."""

    baslik = forms.CharField(label="Başlık", max_length=140)
    etiket = forms.ChoiceField(label="Etiket")
    ozet = forms.CharField(
        label="Özet",
        max_length=300,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Gündem listesinde başlığın altında görünür. En fazla 300 karakter.",
    )
    govde = forms.CharField(label="Metin", required=False, widget=forms.Textarea(attrs={"rows": 14}))
    etkinlik_baslangic = forms.DateTimeField(
        label="Etkinlik tarihi ve saati",
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    etkinlik_yer = forms.CharField(label="Etkinlik yeri", max_length=200, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.duyurular.models import Etiket

        self.fields["etiket"].choices = Etiket.choices

    def clean(self):
        temiz = super().clean()
        from apps.duyurular.models import Etiket

        if temiz.get("etiket") == Etiket.ETKINLIK:
            zaman, yer = temiz.get("etkinlik_baslangic"), (temiz.get("etkinlik_yer") or "").strip()
            if zaman and not yer:
                self.add_error("etkinlik_yer", "Etkinliğin yerini yazın (ör. salon adı veya “Çevrim içi”).")
            if yer and not zaman:
                self.add_error("etkinlik_baslangic", "Etkinliğin tarihini ve saatini girin.")
        return temiz

    def duyuru_verisi(self) -> dict:
        return {k: self.cleaned_data[k] for k in ("baslik", "etiket", "ozet", "govde")}

    def etkinlik_bilgisi(self) -> dict | None:
        zaman, yer = self.cleaned_data.get("etkinlik_baslangic"), (self.cleaned_data.get("etkinlik_yer") or "").strip()
        return {"baslangic": zaman, "yer": yer} if zaman and yer else None


class DuzeltmeFormu(forms.Form):
    not_ = forms.CharField(
        label="Neyin düzeltilmesi gerekiyor?",
        max_length=2000,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Not hazırlayan kişiye panelde gösterilir.",
    )


class DonemFormu(forms.Form):
    ad = forms.CharField(label="Dönem adı", max_length=40, help_text="ör. 2026–2027")
    baslangic = forms.DateField(label="Başlangıç", widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    bitis = forms.DateField(
        label="Bitiş", widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        help_text="Genellikle bir sonraki Olağan Genel Kurul.",
    )
    baslangic_icerigi = forms.ChoiceField(
        label="Nasıl başlasın?",
        widget=forms.RadioSelect,
        choices=[
            ("kopyala", "Önceki dönemin gruplarını ve kişilerini kopyala (sonra düzenlersiniz)"),
            ("varsayilan", "Sitedeki bölümlerle boş başlat (Akademik Danışman, Yönetim, dört birim)"),
            ("bos", "Tamamen boş başlat"),
        ],
        initial="kopyala",
    )


class GrupFormu(forms.Form):
    ad = forms.CharField(label="Grup adı", max_length=120, help_text="ör. İletişim Birimi")
    tur = forms.ChoiceField(label="Tür")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.ekip.models import GrupTuru

        self.fields["tur"].choices = GrupTuru.choices


class KisiFormu(forms.Form):
    ad = forms.CharField(label="Ad soyad", max_length=150)
    gorev = forms.CharField(label="Görev", max_length=100, help_text="ör. Başkan, Birim Sorumlusu, Üye")
    birim = forms.CharField(
        label="Fakülte / bölüm", max_length=200, required=False, help_text="Akademik danışman için."
    )
    eposta = forms.EmailField(label="E-posta", required=False)
    foto = forms.FileField(
        label="Fotoğraf",
        required=False,
        widget=forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
        help_text="JPEG, PNG veya WebP, en fazla 10 MB. Kare kırpılır; konum gibi gizli bilgiler silinir.",
    )
    foto_kaldir = forms.BooleanField(label="Fotoğrafı kaldır", required=False)
    yayin_onayi = forms.BooleanField(
        label="Kişinin yayın için yazılı onayı alındı",
        required=False,
        help_text="İşaretli değilse kişi sitede görünmez (KVKK). Onay belgesini topluluk dosyasında saklayın.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.ekip.models import BAGLANTI_TURLERI

        for tur, ad in BAGLANTI_TURLERI.items():
            self.fields[f"baglanti_{tur}"] = forms.URLField(
                label=ad, required=False, max_length=300, assume_scheme="https",
                widget=forms.URLInput(attrs={"placeholder": "https://…"}),
            )

    def baglanti_alanlari(self):
        return [self[a] for a in self.fields if a.startswith("baglanti_")]

    def clean(self):
        temiz = super().clean()
        for ad, deger in list(temiz.items()):
            if ad.startswith("baglanti_") and deger and not deger.startswith("https://"):
                self.add_error(ad, "Adres https:// ile başlamalı.")
        return temiz

    def kisi_verisi(self, onceki_onay_tarihi=None) -> dict:
        from django.utils import timezone

        v = self.cleaned_data
        return {
            "ad": v["ad"],
            "gorev": v["gorev"],
            "birim": v["birim"],
            "eposta": v["eposta"],
            "baglantilar": {
                a.removeprefix("baglanti_"): d for a, d in v.items() if a.startswith("baglanti_") and d
            },
            "yayin_onayi_tarihi": (onceki_onay_tarihi or timezone.localdate()) if v["yayin_onayi"] else None,
        }


class EkipOnayFormu(forms.Form):
    ozet = forms.CharField(
        label="Değişikliği bir cümleyle özetleyin",
        max_length=300,
        help_text="Yönetim Kurulu onay ekranında görür. ör. “İletişim Birimi'ne iki yeni üye eklendi.”",
    )
