"""pytest ayarları. CI'da ve `docker compose run --rm web pytest` ile kullanılır."""

from .development import *  # noqa: F403

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # yalnızca testleri hızlandırmak için
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
# Testler Redis gerektirmez (CI'da Redis servisi yok); aynı önbellek API'si bellekte.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
