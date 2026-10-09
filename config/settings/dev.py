from .base import *
import environ

environ.Env.read_env(BASE_DIR / ".env.dev")

env = environ.Env()

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "apps.account.backends.EmailOrUsernameBackend",
]


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

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
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS')
DATABASES = {
    'default': env.db('DATABASE_URL')
}

SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT')
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE')
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE')
SECURE_HSTS_SECONDS = env('SECURE_HSTS_SECONDS')

# SimpleJWT настройки
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env('ACCESS_TOKEN_LIFETIME_MINUTES')),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env('REFRESH_TOKEN_LIFETIME_DAYS')),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

