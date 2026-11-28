"""Tüm ortamlar için ortak ayarlar. Ortama özel olanlar development.py, production.py, test.py'de."""

from datetime import timedelta
from pathlib import Path

from .ortam import env

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "axes",
    "apps.accounts",
    "apps.denetim",
    "apps.panel",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "apps.panel.middleware.OturumSuresiMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Kilitli hesap yanıtını üretir; listenin sonunda durmalıdır.
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.panel.baglam.menu",
            ],
        },
    },
]

# Veritabanı: PostgreSQL 17 (OPERASYON.md §3). Şifre dosyadan: DB_PASSWORD_FILE.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", "diyak"),
        "USER": env("DB_USER", "diyak"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", "db"),
        "PORT": env("DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Kullanıcılar e-posta ile giriş yapar (PANEL.md §6).
AUTH_USER_MODEL = "accounts.Kullanici"
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",  # kilitli hesabı şifre denetiminden önce durdurur
    "django.contrib.auth.backends.ModelBackend",
]
LOGIN_URL = "panel:giris"
LOGIN_REDIRECT_URL = "panel:ana"

# Panelin dışarıdan görünen adresi; e-postalardaki bağlantılar bundan üretilir.
PANEL_ADRESI = env("PANEL_ADRESI", "http://localhost:8000").rstrip("/")

# 2FA (PANEL.md §9): TOTP, telefon uygulamasıyla. Hatalı kodlarda django-otp bekleme süresi uygular.
OTP_TOTP_ISSUER = "DİYAK Panel"

# Hatalı giriş kilidi (PANEL.md §9): aynı e-postayla 5 hatalı şifrede 30 dakika kilit.
# IP adresi saklanmaz (PANEL.md §6); kilit yalnızca e-postaya göre uygulanır.
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCKOUT_PARAMETERS = ["username"]
AXES_USERNAME_CALLABLE = "apps.panel.guvenlik.axes_kullanici_adi"
AXES_CLIENT_IP_CALLABLE = "apps.panel.guvenlik.ip_saklanmaz"
AXES_RESET_ON_SUCCESS = True
AXES_DISABLE_ACCESS_LOG = True
AXES_VERBOSE = False  # loglara e-posta yazılmasın
AXES_LOCKOUT_TEMPLATE = "panel/kilitli.html"
# axes.W006 "ip_address yok" uyarısı: IP bilinçli olarak saklanmıyor. Axes, aynı e-postaya ait
# denemeleri tarayıcı bilgisinden bağımsız toplar; tarayıcı değiştirerek kilit atlatılamaz
# (apps/panel/tests/test_giris.py).
SILENCED_SYSTEM_CHECKS = ["axes.W006"]

# Şifre en az 12 karakter, yaygın şifre listesi dahil (PANEL.md §9).
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Oturum: en fazla 8 saat veya 1 saat hareketsizlik, çerezler HttpOnly ve SameSite=Lax (PANEL.md §9).
# Her iki süre de apps.panel.middleware.OturumSuresiMiddleware ile sunucuda uygulanır.
SESSION_COOKIE_AGE = 8 * 60 * 60
PANEL_OTURUM_EN_UZUN = 8 * 60 * 60
PANEL_HAREKETSIZLIK = 60 * 60
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# API (K-23): yalnızca JSON, varsayılan izin KAPALI. Herkese açık uç noktalar görünüm
# düzeyinde açıkça AllowAny alır ve salt okunurdur.
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAdminUser"],
    "UNAUTHENTICATED_USER": None,
}

# Loglara kişisel veri yazılmaz (PANEL.md §9). İstek gövdeleri loglanmaz.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {"axes": {"level": "ERROR"}},
}
