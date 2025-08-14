from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "django-insecure-iqi0*dn_@=xr_3@h2w64j!gwx&9fg2l-cj0rvfzk8f8dg(n42m"

DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    # apps
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]
INSTALLED_APPS += [
    'rest_framework_simplejwt.token_blacklist',
]


ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
CORS_ALLOW_HEADERS = [
    "content-type",
    "authorization",
]
CORS_ALLOW_CREDENTIALS = True


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kathmandu"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.Account"


REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "DEFAULT_AUTHENTICATION_CLASSES": {
        "utilities.jwt_authentication.CustomJWTAuthentication",
    },
    "DEFAULT_PERMISSION_CLASSES": {
        "utilities.permission.CustomPermission",
    },
    "EXCEPTION_HANDLER": "utilities.exception.custom_exception_handler",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
}
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "timestamp": {
            "format": "{asctime} {levelname} {message} {lineno} ",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "debug.log",
            "formatter": "timestamp",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

DEFAULT_FROM_EMAIL = "Jewelry <anishgharti10@gmail.com>"
EMAIL_HOST_USER = "spicyh166@gmail.com"
EMAIL_HOST_PASSWORD = "zjcncrapjofwrrdz"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

PAGE_SIZE = 10


from .jwt_behaviour import *

