import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent



INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "factory-boy",
    # apps
    "apps.accounts",
    "apps.api",
    "apps.catalog",
    "apps.core",
    "apps.delivery",
    "apps.orders",
    "apps.payments",
    "apps.staff",
    "apps.reviews",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


WSGI_APPLICATION = "config.wsgi.application"

AUTH_USER_MODEL = "account.CustomerUser"

LANGUAGE_CODE = "uk"
TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],

    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],

    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',  # Для FilterSet
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
 }

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME' : timedelta(minutes= 30 ),
    'REFRESH_TOKEN_LIFETIME' : timedelta(days= 1 ),
    'ROTATE_REFRESH_TOKENS' : True ,
    'BLACKLIST_AFTER_ROTATION' : True ,
    'UPDATE_LAST_LOGIN' : True ,
}






# SPECTACULAR_SETTINGS = {
#     "TITLE": "Hop & Barley API",
#     "DESCRIPTION": (
#         "REST API інтернет-магазину. Авторизація: `POST /api/users/login/` → "
#         "кнопка **Authorize** → `access`-токен. Кошик живе в сесії, як на сайті."
#     ),
#     "VERSION": "1.0.0",
#     "SERVE_INCLUDE_SCHEMA": False,
#     "COMPONENT_SPLIT_REQUEST": True,  # separate schemas for request and response bodies
#     "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},
#     # Order.delivery_type and User.np_delivery_type share one set of choices
#     "ENUM_NAME_OVERRIDES": {"DeliveryTypeEnum": "apps.delivery.models.DeliveryType"},
# }