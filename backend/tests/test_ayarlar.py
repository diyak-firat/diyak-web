"""K-23 ve PANEL.md §9'daki güvenli varsayılanların bozulmadığını denetler."""

from django.conf import settings


def test_api_varsayilan_izni_kapali():
    assert settings.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] == [
        "rest_framework.permissions.IsAdminUser"
    ]
    assert settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] == []


def test_api_yalnizca_json_doner():
    # Tarayıcıdan gezilebilen API (BrowsableAPIRenderer) kapalı olmalı.
    assert settings.REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] == [
        "rest_framework.renderers.JSONRenderer"
    ]


def test_sifre_en_az_12_karakter():
    uzunluk = next(
        v for v in settings.AUTH_PASSWORD_VALIDATORS if v["NAME"].endswith("MinimumLengthValidator")
    )
    assert uzunluk["OPTIONS"]["min_length"] >= 12


def test_oturum_en_fazla_8_saat_ve_cerezler_guvenli():
    assert settings.SESSION_COOKIE_AGE <= 8 * 60 * 60
    assert settings.SESSION_COOKIE_HTTPONLY is True
    assert settings.SESSION_COOKIE_SAMESITE == "Lax"


def test_kullanici_modeli():
    assert settings.AUTH_USER_MODEL == "accounts.Kullanici"
