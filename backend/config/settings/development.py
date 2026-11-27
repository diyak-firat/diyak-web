"""Yerel geliştirme (docker-compose.dev.yml). Gerçek kişisel veri kullanılmaz; sahte veri ile çalışılır."""

import os

os.environ.setdefault("DJANGO_SECRET_KEY", "yerel-gelistirme-anahtari-gizli-degil")

from .base import *  # noqa: E402,F403
from .ortam import env_list  # noqa: E402

DEBUG = True
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", ["localhost", "127.0.0.1"])

# Yerelde e-postalar gönderilmez, konsola yazılır.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
