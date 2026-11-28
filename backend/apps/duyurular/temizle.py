"""Duyuru gövdesinin HTML temizliği (PANEL.md §9). Gövde kaydedilmeden önce her zaman buradan geçer.

İzin listesi: p, br, h2, h3, strong, em, a[href], ul, ol, li, blockquote. Bağlantılar yalnızca
``https:`` ve ``mailto:`` olabilir ve ``rel="noopener noreferrer"`` alır.
"""

import nh3

ETIKETLER = frozenset({"p", "br", "h2", "h3", "strong", "em", "a", "ul", "ol", "li", "blockquote"})
IZINLI_ADRES_ONEKLERI = ("https://", "mailto:")


def _adres_suzgeci(etiket: str, nitelik: str, deger: str) -> str | None:
    if etiket == "a" and nitelik == "href":
        return deger if deger.strip().lower().startswith(IZINLI_ADRES_ONEKLERI) else None
    return deger


def html_temizle(html: str) -> str:
    return nh3.clean(
        html or "",
        tags=set(ETIKETLER),
        clean_content_tags={"script", "style"},
        attributes={"a": {"href"}},
        url_schemes={"https", "mailto"},
        attribute_filter=_adres_suzgeci,
        link_rel="noopener noreferrer",
        strip_comments=True,
    ).strip()
