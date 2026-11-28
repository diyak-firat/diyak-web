"""Duyuru ve onay akışı (PANEL.md §4, §8; A2 kabul: editör yayımlayamaz, YK yayımlar)."""

from datetime import timedelta

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from apps.accounts.models import Rol
from apps.denetim.models import Eylem, IslemKaydi
from apps.duyurular import servisler
from apps.duyurular.models import Durum, Duyuru, Etiket, turkce_slug
from apps.onay import akis

pytestmark = pytest.mark.django_db

VERI = {"baslik": "Okuma grubu başlıyor", "etiket": Etiket.DUYURU, "ozet": "Kısa özet.", "govde": "<p>Metin</p>"}


@pytest.fixture
def editor(kullanici_yap):
    return kullanici_yap(Rol.EDITOR, "İletişim Birimi", email="editor@ornek.org")


@pytest.fixture
def yk(kullanici_yap):
    return kullanici_yap(Rol.YONETIM_KURULU, "Sayman", email="yk@ornek.org")


@pytest.fixture
def taslak(editor):
    return servisler.kaydet_duyuru(editor, VERI)


def test_turkce_slug():
    assert turkce_slug("Çağrı: Şubat'ta İğdır ve Ödül Günü!") == "cagri-subatta-igdir-ve-odul-gunu"
    assert turkce_slug("!!!") == "duyuru"


def test_slug_benzersiz_ve_sabit(editor):
    a = servisler.kaydet_duyuru(editor, VERI)
    b = servisler.kaydet_duyuru(editor, VERI)
    assert (a.slug, b.slug) == ("okuma-grubu-basliyor", "okuma-grubu-basliyor-2")
    a = servisler.kaydet_duyuru(editor, {"baslik": "Yeni başlık"}, a)
    assert a.slug == "okuma-grubu-basliyor"


def test_editor_taslak_yazar_ve_onaya_gonderir_ama_yayimlayamaz(editor, taslak):
    assert taslak.durum == Durum.TASLAK and taslak.olusturan == editor
    akis.onaya_gonder(editor, taslak)
    taslak.refresh_from_db()
    assert taslak.durum == Durum.ONAY_BEKLIYOR
    with pytest.raises(PermissionDenied):
        akis.onayla(editor, taslak)
    taslak.refresh_from_db()
    assert taslak.durum == Durum.ONAY_BEKLIYOR and taslak.yayin_tarihi is None


def test_yk_onaylar_ve_yayimlar(editor, yk, taslak):
    akis.onaya_gonder(editor, taslak)
    akis.onayla(yk, taslak)
    taslak.refresh_from_db()
    assert taslak.durum == Durum.YAYINDA and taslak.onaylayan == yk and taslak.yayin_tarihi is not None
    eylemler = list(IslemKaydi.objects.order_by("id").values_list("eylem", "kullanici_id", "ayrinti"))
    assert eylemler == [(Eylem.ONAYA_GONDERME, editor.pk, {}), (Eylem.ONAYLAMA, yk.pk, {})]


def test_yk_kendi_icerigini_onaylar_ve_kayitta_gorunur(yk):
    d = servisler.kaydet_duyuru(yk, VERI)
    akis.onaya_gonder(yk, d)
    akis.onayla(yk, d)
    assert IslemKaydi.objects.get(eylem=Eylem.ONAYLAMA).ayrinti == {"kendi_icerigi": True}


@pytest.mark.parametrize("rol", [Rol.DANISMAN, Rol.TEKNIK, None])
def test_editor_ve_yk_disindakiler_hicbir_sey_yapamaz(kullanici_yap, taslak, editor, rol):
    k = kullanici_yap(rol)
    with pytest.raises(PermissionDenied):
        servisler.kaydet_duyuru(k, VERI)
    with pytest.raises(PermissionDenied):
        servisler.kaydet_duyuru(k, {"baslik": "x"}, taslak)
    with pytest.raises(PermissionDenied):
        akis.onaya_gonder(k, taslak)
    akis.onaya_gonder(editor, taslak)
    with pytest.raises(PermissionDenied):
        akis.onayla(k, taslak)
    with pytest.raises(PermissionDenied):
        akis.duzeltme_iste(k, taslak, "not")


def test_suresi_dolmus_yk_onaylayamaz(kullanici_yap, editor, taslak):
    dun = timezone.localdate() - timedelta(days=1)
    eski = kullanici_yap(Rol.YONETIM_KURULU, "Başkan", baslangic=dun - timedelta(days=300), bitis=dun)
    akis.onaya_gonder(editor, taslak)
    with pytest.raises(PermissionDenied):
        akis.onayla(eski, taslak)


def test_duzeltme_iste_taslaga_doner_ve_not_kalir(editor, yk, taslak):
    akis.onaya_gonder(editor, taslak)
    with pytest.raises(ValidationError):
        akis.duzeltme_iste(yk, taslak, "  ")
    akis.duzeltme_iste(yk, taslak, "Tarihi ekleyin.")
    taslak.refresh_from_db()
    assert taslak.durum == Durum.TASLAK and taslak.onay_notu == "Tarihi ekleyin."
    akis.onaya_gonder(editor, taslak)
    taslak.refresh_from_db()
    assert taslak.onay_notu == ""


def test_eksik_duyuru_onaya_gonderilemez(editor):
    d = servisler.kaydet_duyuru(editor, {**VERI, "govde": "<script>x</script>"})
    with pytest.raises(ValidationError, match="Metin boş"):
        akis.onaya_gonder(editor, d)


def test_etkinlik_etiketi_zaman_ve_yer_ister(editor, yk):
    d = servisler.kaydet_duyuru(editor, {**VERI, "etiket": Etiket.ETKINLIK})
    with pytest.raises(ValidationError, match="etkinlik zamanı"):
        akis.onaya_gonder(editor, d)
    zaman = timezone.now() + timedelta(days=7)
    d = servisler.kaydet_duyuru(editor, {}, d, etkinlik_bilgisi={"baslangic": zaman, "yer": "[Salon]"})
    assert d.etkinlik.yer == "[Salon]" and d.etkinlik.ad == VERI["baslik"]
    d = servisler.kaydet_duyuru(editor, {"baslik": "Yeni ad"}, d, etkinlik_bilgisi={"baslangic": zaman, "yer": "[Salon 2]"})
    d.etkinlik.refresh_from_db()
    assert (d.etkinlik.ad, d.etkinlik.yer) == ("Yeni ad", "[Salon 2]")
    akis.onaya_gonder(editor, d)


def test_onay_bekleyen_duzenlenemez_geri_cekilir(editor, kullanici_yap, taslak):
    akis.onaya_gonder(editor, taslak)
    with pytest.raises(PermissionDenied):
        servisler.kaydet_duyuru(editor, {"baslik": "x"}, taslak)
    baska_editor = kullanici_yap(Rol.EDITOR)
    with pytest.raises(PermissionDenied):
        akis.geri_cek(baska_editor, taslak)
    akis.geri_cek(editor, taslak)
    taslak.refresh_from_db()
    assert taslak.durum == Durum.TASLAK


def test_yayindaki_duyuruyu_editor_degistiremez_yk_degistirir(editor, yk, taslak):
    akis.onaya_gonder(editor, taslak)
    akis.onayla(yk, taslak)
    with pytest.raises(PermissionDenied):
        servisler.kaydet_duyuru(editor, {"baslik": "Sessiz değişiklik"}, taslak)
    servisler.kaydet_duyuru(yk, {"ozet": "Düzeltilmiş özet."}, taslak)
    taslak.refresh_from_db()
    assert taslak.durum == Durum.YAYINDA and taslak.ozet == "Düzeltilmiş özet."
    assert IslemKaydi.objects.filter(eylem=Eylem.YAYIMLAMA, ayrinti={"yayindaki_duzenleme": True}).exists()


def test_yayindan_kaldirma_ve_yeniden_onay(editor, yk, taslak):
    akis.onaya_gonder(editor, taslak)
    akis.onayla(yk, taslak)
    ilk_yayin = Duyuru.objects.get(pk=taslak.pk).yayin_tarihi
    with pytest.raises(PermissionDenied):
        servisler.yayindan_kaldir(editor, taslak)
    servisler.yayindan_kaldir(yk, taslak)
    taslak.refresh_from_db()
    assert taslak.durum == Durum.KALDIRILDI
    # Kaldırılan duyuru düzenlenince taslağa döner; yeniden onaysız yayına çıkamaz.
    d = servisler.kaydet_duyuru(editor, {"ozet": "Güncel."}, taslak)
    assert d.durum == Durum.TASLAK
    akis.onaya_gonder(editor, d)
    akis.onayla(yk, d)
    d.refresh_from_db()
    assert d.yayin_tarihi == ilk_yayin
    with pytest.raises(ValidationError):
        servisler.sil(yk, d)


def test_onaylanmis_icerik_ikinci_kez_onaylanamaz(editor, yk, taslak):
    akis.onaya_gonder(editor, taslak)
    akis.onayla(yk, taslak)
    with pytest.raises(ValidationError):
        akis.onayla(yk, taslak)
    with pytest.raises(ValidationError):
        akis.onaya_gonder(editor, taslak)


def test_taslak_silme(editor, kullanici_yap, yk, taslak):
    with pytest.raises(PermissionDenied):
        servisler.sil(kullanici_yap(Rol.EDITOR), taslak)
    servisler.sil(editor, taslak)
    assert not Duyuru.objects.exists()
    d = servisler.kaydet_duyuru(editor, VERI)
    servisler.sil(yk, d)
    assert not Duyuru.objects.exists()
