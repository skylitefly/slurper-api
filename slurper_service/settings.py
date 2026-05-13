import os
from pathlib import Path

from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SKYLITE_DJANGO_SECRET_KEY", "django-insecure-slurper-service")
DEBUG = os.getenv("SKYLITE_DJANGO_DEBUG", "false") == "true"
ALLOWED_HOSTS = os.getenv(
    "SKYLITE_DJANGO_ALLOWED_HOSTS",
    "slurper.skylitefly.com,localhost,127.0.0.1",
).split(",")

INSTALLED_APPS = [
    "corsheaders",
    "slurper.apps.SlurperConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "slurper_service.urls"
WSGI_APPLICATION = "slurper_service.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
STATIC_URL = "static/"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

redis_location = os.getenv("SKYLITE_REDIS_DEFAULT_LOCATION")
if redis_location:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": redis_location,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PASSWORD": os.getenv("SKYLITE_REDIS_DEFAULT_PASSWORD", None) or None,
                "SOCKET_CONNECT_TIMEOUT": 5,
                "SOCKET_TIMEOUT": 5,
            },
            "KEY_PREFIX": os.getenv("SKYLITE_REDIS_DEFAULT_KEY_PREFIX", "slurper"),
            "TIMEOUT": 60,
        }
    }
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = list(default_headers)

SLURPER_WHAZZUP_URL = os.getenv(
    "SKYLITE_SLURPER_WHAZZUP_URL",
    "https://fsddata.skylitefly.com/whazzup.json",
)
SLURPER_WHAZZUP_TIMEOUT_SECONDS = int(os.getenv("SKYLITE_SLURPER_WHAZZUP_TIMEOUT_SECONDS", "5"))
SLURPER_WHAZZUP_CACHE_SECONDS = int(os.getenv("SKYLITE_SLURPER_WHAZZUP_CACHE_SECONDS", "5"))
