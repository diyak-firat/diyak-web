"""pytest ayarları. CI'da ve `docker compose run --rm web pytest` ile kullanılır."""

from .development import *  # noqa: F403

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # yalnızca testleri hızlandırmak için
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
