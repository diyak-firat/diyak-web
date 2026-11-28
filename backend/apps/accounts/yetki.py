"""Panel yetki kuralları (PANEL.md §4).

Yetki yalnızca **etkin** rol atamalarından gelir: bitiş tarihi geçmiş atama, kapatılmış hesap
veya ``is_superuser`` panelde hiçbir yetki vermez. Görünümler bu fonksiyonları kullanır;
kendi kontrolünü yazmaz.
"""

from .models import ATAMA_YETKILI_GOREVLER, Rol, RolAtamasi

# Başkan ve Başkan Yardımcısı'nın atayabildiği roller. Teknik rolünü yalnızca teknik
# sorumlular yönetir (görev ayrılığı: hesap bakımı içerik yönetiminden ayrı tutulur).
BASKANLIGIN_ATAYABILDIGI = frozenset({Rol.YONETIM_KURULU, Rol.EDITOR, Rol.DANISMAN})
TEKNIGIN_ATAYABILDIGI = frozenset({Rol.TEKNIK})


def _giris_yapmis(kullanici) -> bool:
    return kullanici is not None and kullanici.is_authenticated and kullanici.is_active


def etkin_roller(kullanici, gun=None) -> set[str]:
    if not _giris_yapmis(kullanici):
        return set()
    return set(RolAtamasi.objects.etkin(gun).filter(kullanici=kullanici).values_list("rol", flat=True))


def rolu_var(kullanici, *roller: str, gun=None) -> bool:
    return bool(etkin_roller(kullanici, gun) & set(roller))


def panel_kullanicisi_mi(kullanici, gun=None) -> bool:
    """Etkin en az bir rolü olan kişi panele girebilir (2FA ayrıca zorunludur)."""
    return bool(etkin_roller(kullanici, gun))


def baskan_veya_yardimcisi_mi(kullanici, gun=None) -> bool:
    if not _giris_yapmis(kullanici):
        return False
    return (
        RolAtamasi.objects.etkin(gun)
        .filter(kullanici=kullanici, rol=Rol.YONETIM_KURULU, gorev_adi__in=ATAMA_YETKILI_GOREVLER)
        .exists()
    )


def atanabilir_roller(kullanici, gun=None) -> frozenset[str]:
    """Bu kişinin davet edebildiği, atayabildiği ve kaldırabildiği roller."""
    roller: set[str] = set()
    if baskan_veya_yardimcisi_mi(kullanici, gun):
        roller |= BASKANLIGIN_ATAYABILDIGI
    if rolu_var(kullanici, Rol.TEKNIK, gun=gun):
        roller |= TEKNIGIN_ATAYABILDIGI
    return frozenset(roller)


def rol_atayabilir_mi(kullanici, rol: str, gun=None) -> bool:
    return rol in atanabilir_roller(kullanici, gun)


def kullanicilari_yonetebilir_mi(kullanici, gun=None) -> bool:
    """Kullanıcılar ekranını açabilir mi (Başkan, Başkan Yrd., Teknik)."""
    return bool(atanabilir_roller(kullanici, gun))


def teknik_mi(kullanici, gun=None) -> bool:
    """2FA sıfırlama ve hesap kilidini açma yalnızca teknik sorumlunundur (PANEL.md §4)."""
    return rolu_var(kullanici, Rol.TEKNIK, gun=gun)


def hesabi_kapatabilir_mi(kapatan, hedef, gun=None) -> bool:
    """Kendi hesabını kimse kapatamaz. Hedefin etkin rollerinin hepsini yönetebilen kişi kapatır;
    hiç rolü olmayan hesabı Başkan veya Başkan Yardımcısı kapatır.
    """
    if hedef.pk == getattr(kapatan, "pk", None) or not hedef.is_active:
        return False
    roller = etkin_roller(hedef, gun)
    if not roller:
        return baskan_veya_yardimcisi_mi(kapatan, gun)
    return roller <= atanabilir_roller(kapatan, gun)
