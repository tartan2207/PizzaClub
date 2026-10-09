from .base import *
import environ


environ.Env.read_env(BASE_DIR / ".env.production")

env = environ.Env()

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

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
            ],
        },
    },
]

DATABASES = {
    'default': env.db('DATABASE_URL')
}

# віддає статику (адмінка, restframework, swagger ui, ...) на проді, альтернатива nginx
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},

}


# --- HTTPS behind Caddy (manage.py check --deploy) ----------------------------------
# Caddy terminates TLS and passes the original scheme in X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REDIRECT_EXEMPT = [r"^health/$"]  # the Docker healthcheck calls plain http inside



# --- Logs ---------------------------------------------------------------------------
# With DEBUG=False Django prints errors nowhere by default. Send everything to stdout:
# `docker compose logs web` shows tracebacks and our logger.exception() calls.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {"format": "{asctime} {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "plain"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {"django": {"handlers": ["console"], "level": "INFO", "propagate": False}},
}

CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT')
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE')
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE')
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=3600)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env('SECURE_HSTS_INCLUDE_SUBDOMAINS')
SECURE_HSTS_PRELOAD = env('SECURE_HSTS_PRELOAD')
