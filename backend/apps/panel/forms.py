from django import forms
from django.contrib.auth.forms import AuthenticationForm


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
