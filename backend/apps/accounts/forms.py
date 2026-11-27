from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Kullanici


class KullaniciOlusturmaFormu(UserCreationForm):
    class Meta:
        model = Kullanici
        fields = ("email",)


class KullaniciDegistirmeFormu(UserChangeForm):
    class Meta:
        model = Kullanici
        fields = ("email", "first_name", "last_name")
