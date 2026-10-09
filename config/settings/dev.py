from .base import *

environ.Env.read_env(BASE_DIR / ".env.dev")

env = environ.Env()

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS" )

CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')

DATABASES = {
    'default': env.db('DATABASE_URL')
}


