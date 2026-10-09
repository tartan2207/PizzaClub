from .base import *

environ.Env.read_env(BASE_DIR / ".env.production")

env = environ.Env()

SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS" )

CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')

DATABASES = {
    'default': env.db('DATABASE_URL')
}


DEBUG = False

# віддає статику (адмінка, restframework, swagger ui, ...) на проді, альтернатива nginx
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},

}


# --- HTTPS behind Caddy (manage.py check --deploy) ----------------------------------
# Caddy terminates TLS and passes the original scheme in X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r"^health/$"]  # the Docker healthcheck calls plain http inside
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# HSTS: the browser goes straight to https next time. Start small, raise to a year
# (31536000) when you are sure HTTPS works.
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=3600)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True