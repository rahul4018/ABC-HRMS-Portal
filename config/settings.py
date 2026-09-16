import os
from pathlib import Path
from urllib.parse import urlsplit, unquote
from datetime import timedelta

from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-change-this-later",
)

DEBUG = config(
    "DEBUG",
    cast=bool,
    default=True,
)

# Render provides the hostname through the ALLOWED_HOSTS
# environment variable. Local development remains available.
_allowed_hosts_raw = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,.onrender.com",
)

ALLOWED_HOSTS = [
    host.strip()
    for host in _allowed_hosts_raw.split(",")
    if host.strip()
]


# CSRF trusted origins for deployed HTTPS environments.
_csrf_origins_raw = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
)

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in _csrf_origins_raw.split(",")
    if origin.strip()
]


# Production security settings.
if not DEBUG:
    SECURE_SSL_REDIRECT = config(
        "SECURE_SSL_REDIRECT",
        cast=bool,
        default=True,
    )

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SECURE_HSTS_SECONDS = config(
        "SECURE_HSTS_SECONDS",
        cast=int,
        default=0,
    )

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = False

    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"


# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # REST API
    "rest_framework",
    "rest_framework_simplejwt",

    # HRMS apps
    "apps.accounts",
    "apps.employees",
    "apps.documents",
    "apps.payslips",
    "apps.leave",
    "apps.dashboard",
    "apps.reports",
    "apps.workforce",

    # Other apps
    "resignation",
    "appraisal",
    "promotions",
    "requestsystem",
    "notifications",
    "recruitment",
    "audit",
    "api",
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise serves collected static files in production.
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    # Custom HRMS first-login password enforcement.
    "skillconnect_security_middleware.ForcePasswordChangeMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================================================
# URL / APPLICATION CONFIGURATION
# =========================================================

ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

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


WSGI_APPLICATION = "config.wsgi.application"


# =========================================================
# DATABASE - POSTGRESQL / SUPABASE
# =========================================================
#
# Priority:
# 1. DATABASE_URL - used by Render/Supabase
# 2. DB_* variables - useful for local development
#

DATABASE_URL = os.environ.get("DATABASE_URL")


if DATABASE_URL:
    _abc_db = urlsplit(DATABASE_URL)

    if _abc_db.scheme not in {"postgresql", "postgres"}:
        raise RuntimeError(
            "DATABASE_URL must be a PostgreSQL/Supabase connection URL."
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(_abc_db.path.lstrip("/")),
            "USER": unquote(_abc_db.username or ""),
            "PASSWORD": unquote(_abc_db.password or ""),
            "HOST": _abc_db.hostname or "",
            "PORT": str(_abc_db.port or 5432),
            "CONN_MAX_AGE": 600,
            "OPTIONS": {
                "sslmode": "require",
            },
        }
    }

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",

            "NAME": config(
                "DB_NAME",
                default="postgres",
            ),

            "USER": config(
                "DB_USER",
                default="postgres",
            ),

            "PASSWORD": config(
                "DB_PASSWORD",
                default="",
            ),

            "HOST": config(
                "DB_HOST",
                default="127.0.0.1",
            ),

            "PORT": config(
                "DB_PORT",
                default="5432",
            ),

            "CONN_MAX_AGE": 60,
        }
    }


# =========================================================
# CUSTOM USER MODEL
# =========================================================

AUTH_USER_MODEL = "accounts.User"


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = []


# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# WhiteNoise configuration.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}


# =========================================================
# MEDIA FILES
# =========================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# =========================================================
# AUTHENTICATION / LOGIN
# =========================================================

LOGIN_URL = "/login/"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "/login/"


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================================================
# DJANGO REST FRAMEWORK
# =========================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}


# =========================================================
# SIMPLE JWT
# =========================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),

    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": False,

    "BLACKLIST_AFTER_ROTATION": False,

    "AUTH_HEADER_TYPES": (
        "Bearer",
    ),
}


# =========================================================
# PORTFOLIO / BRAND SETTINGS
# =========================================================

COMPANY_NAME = config(
    "COMPANY_NAME",
    default="ABC HRMS Portal",
)

COMPANY_TAGLINE = config(
    "COMPANY_TAGLINE",
    default="Workforce Management Platform",
)

BRAND_PRIMARY = config(
    "BRAND_PRIMARY",
    default="#1a3a6b",
)

BRAND_ACCENT = config(
    "BRAND_ACCENT",
    default="#f5a623",
)

PORTFOLIO_MODE = config(
    "PORTFOLIO_MODE",
    cast=bool,
    default=True,
)

DEMO_MODE = config(
    "DEMO_MODE",
    cast=bool,
    default=True,
)