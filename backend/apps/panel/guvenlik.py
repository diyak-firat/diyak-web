"""django-axes için küçük ayar fonksiyonları (settings.AXES_*)."""


def ip_saklanmaz(request) -> None:
    """IP adresi kaydedilmez (PANEL.md §6). Kilit yalnızca e-postaya göre uygulanır."""
    return None


def axes_kullanici_adi(request, credentials) -> str:
    """Hatalı denemeler e-postaya göre sayılır; büyük/küçük harf farkı kilidi atlatmasın."""
    deger = ""
    if credentials:
        deger = credentials.get("username") or credentials.get("email") or ""
    if not deger and request is not None:
        deger = request.POST.get("username", "")
    return deger.strip().lower()
