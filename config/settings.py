import os
from urllib.parse import urlsplit, unquote
from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-change-this-later'
)

DEBUG = config(
    'DEBUG',
    cast=bool,
    default=True
)

ALLOWED_HOSTS = ['*']


# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # REST API
    'rest_framework',
    'rest_framework_simplejwt',

    # HRMS apps
    'apps.accounts',
    'apps.employees',
    'apps.documents',
    'apps.payslips',
    'apps.leave',
    'apps.dashboard',
    'apps.reports',
    'apps.workforce',

    # Other apps
    'resignation',
    'appraisal',
    'promotions',
    'requestsystem',
    'notifications',
    'recruitment',
    'audit',
    'api',
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    'skillconnect_security_middleware.ForcePasswordChangeMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =========================================================
# URL / APPLICATION CONFIGURATION
# =========================================================

ROOT_URLCONF = 'config.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'templates',
        ],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'


# =========================================================
# DATABASE - POSTGRESQL
# =========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',

        'NAME': config(
            'DB_NAME',
            default='ABC HRMS Portal_hrms'
        ),

        'USER': config(
            'DB_USER',
            default='postgres'
        ),

        'PASSWORD': config(
            'DB_PASSWORD',
            default='ABC HRMS Portal'
        ),

        'HOST': config(
            'DB_HOST',
            default='127.0.0.1'
        ),

        'PORT': config(
            'DB_PORT',
            default='5432'
        ),

        'CONN_MAX_AGE': 60,
    }
}


# =========================================================
# CUSTOM USER MODEL
# =========================================================

AUTH_USER_MODEL = 'accounts.User'


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = []


# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# =========================================================
# MEDIA FILES
# =========================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# =========================================================
# AUTHENTICATION / LOGIN
# =========================================================

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/login/'


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =========================================================
# DJANGO REST FRAMEWORK
# =========================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


# =========================================================
# SIMPLE JWT
# =========================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),

    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),

    'ROTATE_REFRESH_TOKENS': False,

    'BLACKLIST_AFTER_ROTATION': False,

    'AUTH_HEADER_TYPES': (
        'Bearer',
    ),
}

# ABC_HRMS_SUPABASE_DATABASE_CONFIG
# Uses Supabase PostgreSQL when DATABASE_URL is present; otherwise the existing
# local database configuration remains available for local development.
_abc_database_url = os.environ.get("DATABASE_URL")
if _abc_database_url:
    _abc_db = urlsplit(_abc_database_url)
    if _abc_db.ABCeme not in {"postgresql", "postgres"}:
        raise RuntimeError("DATABASE_URL must be a PostgreSQL/Supabase connection URL.")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(_abc_db.path.lstrip("/")),
            "USER": unquote(_abc_db.username or ""),
            "PASSWORD": unquote(_abc_db.password or ""),
            "HOST": _abc_db.hostname or "",
            "PORT": str(_abc_db.port or 5432),
            "OPTIONS": {"sslmode": "require"},
        }
    }
