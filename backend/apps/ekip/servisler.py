"""Ekip sayfası işlemleri: dönem, grup ve kişi düzenleme; onaya gönderme (PANEL.md §8).

Düzenlemeyi Editör ve Yönetim Kurulu yapar; onayı Yönetim Kurulu verir (apps.onay.akis).
"""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Max

from apps.accounts.yetki import icerik_hazirlayabilir_mi
from apps.onay import akis

from .foto import foto_isle
from .models import Degisiklik, DegisiklikDurumu, Donem, Grup, GrupTuru, Kisi

KISI_ALANLARI = ("ad", "gorev", "birim", "eposta", "baglantilar", "yayin_onayi_tarihi")

# Sitedeki ekip sayfasının bölümleri (DESIGN.md "Ekip"; frontend/src/data/ekip.json). Yeni dönem
# "sitedeki yapıyla" başlatılınca bu gruplar boş olarak açılır.
VARSAYILAN_GRUPLAR = (
    ("Akademik Danışman", GrupTuru.DANISMAN),
    ("Yönetim", GrupTuru.YONETIM),
    ("Proje ve Araştırma Birimi", GrupTuru.BIRIM),
    ("İletişim Birimi", GrupTuru.BIRIM),
    ("Etkinlik ve Sponsorluk Birimi", GrupTuru.BIRIM),
    ("Medya ve Tasarım Birimi", GrupTuru.BIRIM),
)


def _yetki(kullanici) -> None:
    if not icerik_hazirlayabilir_mi(kullanici):
        raise PermissionDenied("Ekip sayfasını düzenleme yetkiniz yok.")


def aktif_donem() -> Donem | None:
    return Donem.objects.filter(aktif=True).first()


@transaction.atomic
def donem_olustur(
    kullanici, ad: str, baslangic, bitis, kopyalanacak: Donem | None = None, varsayilan_gruplar: bool = False
) -> Donem:
    """Yeni dönemi açar ve aktif yapar. ``kopyalanacak`` verilirse gruplar ve kişiler kopyalanır;
    ``varsayilan_gruplar`` ise sitedeki bölümler boş olarak açılır."""
    _yetki(kullanici)
    if bitis < baslangic:
        raise ValidationError("Dönemin bitişi başlangıcından önce olamaz.")
    if Donem.objects.filter(ad=ad.strip()).exists():
        raise ValidationError("Bu adla bir dönem zaten var.")
    Donem.objects.filter(aktif=True).update(aktif=False)
    donem = Donem.objects.create(ad=ad.strip(), baslangic=baslangic, bitis=bitis, aktif=True)
    if kopyalanacak is not None:
        for grup in kopyalanacak.gruplar.prefetch_related("kisiler"):
            yeni = Grup.objects.create(donem=donem, ad=grup.ad, tur=grup.tur, sira=grup.sira)
            for k in grup.kisiler.all():
                Kisi.objects.create(grup=yeni, foto=k.foto.name, sira=k.sira, kullanici=k.kullanici,
                                    **{a: getattr(k, a) for a in KISI_ALANLARI})
    elif varsayilan_gruplar:
        for sira, (grup_adi, tur) in enumerate(VARSAYILAN_GRUPLAR, start=1):
            Grup.objects.create(donem=donem, ad=grup_adi, tur=tur, sira=sira)
    return donem


def grup_kaydet(kullanici, donem: Donem, ad: str, tur: str, grup: Grup | None = None) -> Grup:
    _yetki(kullanici)
    if grup is None:
        sira = (donem.gruplar.aggregate(m=Max("sira"))["m"] or 0) + 1
        grup = Grup(donem=donem, sira=sira)
    grup.ad, grup.tur = ad.strip(), tur
    grup.full_clean()
    grup.save()
    return grup


def kisi_kaydet(kullanici, grup: Grup, veri: dict, kisi: Kisi | None = None, foto=None, foto_kaldir=False) -> Kisi:
    """``veri``: KISI_ALANLARI. ``foto`` yüklenen dosya ise işlenip yeni dosya olarak kaydedilir."""
    _yetki(kullanici)
    if kisi is None:
        sira = (grup.kisiler.aggregate(m=Max("sira"))["m"] or 0) + 1
        kisi = Kisi(grup=grup, sira=sira)
    for alan in KISI_ALANLARI:
        if alan in veri:
            setattr(kisi, alan, veri[alan])
    if foto is not None:
        kisi.foto = foto_isle(foto)
    elif foto_kaldir:
        kisi.foto = ""
    kisi.full_clean(exclude=["foto"])
    kisi.save()
    return kisi


def sil(kullanici, nesne: Grup | Kisi) -> None:
    """Grubu (içindeki kişilerle) veya kişiyi çalışma kopyasından siler. Yayındaki hal değişmez."""
    _yetki(kullanici)
    nesne.delete()


@transaction.atomic
def tasi(kullanici, nesne: Grup | Kisi, yon: int) -> None:
    """Sırayı bir yukarı (-1) veya aşağı (+1) taşır."""
    _yetki(kullanici)
    kardesler = list(nesne.donem.gruplar.all() if isinstance(nesne, Grup) else nesne.grup.kisiler.all())
    i = next(i for i, k in enumerate(kardesler) if k.pk == nesne.pk)
    j = i + yon
    if not 0 <= j < len(kardesler):
        return
    kardesler[i], kardesler[j] = kardesler[j], kardesler[i]
    for sira, k in enumerate(kardesler, start=1):
        if k.sira != sira:
            k.sira = sira
            k.save(update_fields=["sira"])


def anlik_goruntu(donem: Donem) -> dict:
    """Sitede görünecek içerik: yalnızca yayın onayı olan kişiler ve herkese açık alanlar."""
    gruplar = []
    for grup in donem.gruplar.prefetch_related("kisiler"):
        kisiler = [
            {
                "ad": k.ad,
                "gorev": k.gorev,
                "birim": k.birim,
                "eposta": k.eposta,
                "foto": k.foto.name or None,
                "baglantilar": dict(k.baglantilar),
            }
            for k in grup.kisiler.all()
            if k.yayin_onayi_tarihi is not None
        ]
        gruplar.append({"ad": grup.ad, "tur": grup.tur, "kisiler": kisiler})
    return {"donem": donem.ad, "gruplar": gruplar}


def acik_degisiklik() -> Degisiklik | None:
    return Degisiklik.objects.filter(durum__in=[DegisiklikDurumu.TASLAK, DegisiklikDurumu.ONAY_BEKLIYOR]).first()


@transaction.atomic
def onaya_gonder(kullanici, donem: Donem, ozet: str) -> Degisiklik:
    """Çalışma kopyasının şu anki halini dondurup onaya gönderir.

    Aynı anda tek bir açık değişiklik olur. Düzeltme istenmiş (taslağa dönmüş) değişiklik varsa
    o güncellenip yeniden gönderilir; onay bekleyen varsa önce geri çekilmelidir.
    """
    _yetki(kullanici)
    acik = acik_degisiklik()
    if acik is not None and acik.durum == DegisiklikDurumu.ONAY_BEKLIYOR:
        raise ValidationError("Onay bekleyen bir ekip değişikliği var. Yenisini göndermek için önce onu geri çekin.")
    degisiklik = acik or Degisiklik(olusturan=kullanici)
    degisiklik.donem = donem
    degisiklik.ozet = (ozet or "").strip()[:300]
    degisiklik.veri = anlik_goruntu(donem)
    degisiklik.save()
    return akis.onaya_gonder(kullanici, degisiklik)


def fark(eski: dict | None, yeni: dict) -> list[dict]:
    """Onay ekranı için: gruplara göre eklenen, çıkarılan ve bilgisi değişen kişiler (ada göre)."""
    eski_gruplar = {g["ad"]: {k["ad"]: k for k in g["kisiler"]} for g in (eski or {}).get("gruplar", [])}
    sonuc = []
    for g in yeni.get("gruplar", []):
        onceki = eski_gruplar.pop(g["ad"], None)
        simdiki = {k["ad"]: k for k in g["kisiler"]}
        if onceki is None:
            sonuc.append({"grup": g["ad"], "yeni_grup": True, "eklenen": list(simdiki), "cikan": [], "degisen": []})
            continue
        eklenen = [a for a in simdiki if a not in onceki]
        cikan = [a for a in onceki if a not in simdiki]
        degisen = [a for a in simdiki if a in onceki and simdiki[a] != onceki[a]]
        if eklenen or cikan or degisen:
            sonuc.append({"grup": g["ad"], "yeni_grup": False, "eklenen": eklenen, "cikan": cikan, "degisen": degisen})
    for ad, kisiler in eski_gruplar.items():
        sonuc.append({"grup": ad, "kalkan_grup": True, "eklenen": [], "cikan": list(kisiler), "degisen": []})
    return sonuc


def yayindaki() -> Degisiklik | None:
    return Degisiklik.objects.filter(durum=DegisiklikDurumu.YAYINDA).order_by("-yayin_tarihi").first()
