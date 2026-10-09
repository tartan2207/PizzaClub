from .base import *
import environ

environ.Env.read_env(BASE_DIR / ".env.local")

env = environ.Env()

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "apps.account.backends.EmailOrUsernameBackend",
]

DATABASES = {
    'default': env.db('DATABASE_URL')
}



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
                # "apps.core.context_processors.shop",
                # "apps.orders.context_processors.cart",
            ],
        },
    },
]
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')

