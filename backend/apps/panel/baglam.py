"""Panel şablonlarına menüyü verir. Menüde yalnızca kişinin açabildiği ekranlar görünür."""

from apps.accounts.yetki import islem_kaydini_gorebilir_mi, kullanicilari_yonetebilir_mi, panel_kullanicisi_mi


def menu(request):
    k = getattr(request, "user", None)
    if k is None or not k.is_authenticated or not k.is_verified() or not panel_kullanicisi_mi(k):
        return {}
    eslesme = getattr(request, "resolver_match", None)
    ad = eslesme.url_name if eslesme and eslesme.namespace == "panel" else ""
    ogeler = [("Ana ekran", "panel:ana", ad == "ana")]
    if kullanicilari_yonetebilir_mi(k):
        ogeler.append(("Kullanıcılar", "panel:kullanicilar", ad.startswith("kullanici")))
    if islem_kaydini_gorebilir_mi(k):
        ogeler.append(("İşlem kaydı", "panel:islem_kaydi", ad == "islem_kaydi"))
    ogeler.append(("Hesabım", "panel:hesabim", ad.startswith("hesabim")))
    return {"panel_menu": [{"ad": a, "adres": u, "aktif": aktif} for a, u, aktif in ogeler]}
