"""Ortam değişkenlerini okuyan küçük yardımcılar.

Gizli bilgiler kodda yer almaz. Bir değişken için ``AD_FILE`` verilmişse değer o dosyadan
okunur (Docker secrets: ``/run/secrets/...``). Böylece şifreler ortam değişkenlerinde de
görünmez.
"""

import os

from django.core.exceptions import ImproperlyConfigured

_BOS = object()


def env(ad: str, varsayilan: str | object = _BOS) -> str:
    dosya = os.environ.get(f"{ad}_FILE")
    if dosya:
        try:
            with open(dosya, encoding="utf-8") as f:
                return f.read().strip()
        except OSError as hata:
            raise ImproperlyConfigured(f"{ad}_FILE okunamadı: {dosya}") from hata
    deger = os.environ.get(ad)
    if deger is not None:
        return deger
    if varsayilan is _BOS:
        raise ImproperlyConfigured(f"{ad} ortam değişkeni (veya {ad}_FILE) tanımlı değil.")
    return varsayilan  # type: ignore[return-value]


def env_bool(ad: str, varsayilan: bool = False) -> bool:
    deger = os.environ.get(ad)
    if deger is None:
        return varsayilan
    return deger.strip().lower() in {"1", "true", "evet", "yes", "on"}


def env_list(ad: str, varsayilan: list[str] | None = None) -> list[str]:
    deger = os.environ.get(ad)
    if deger is None:
        return list(varsayilan or [])
    return [parca.strip() for parca in deger.split(",") if parca.strip()]
