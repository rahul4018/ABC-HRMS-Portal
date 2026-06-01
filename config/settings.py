from pathlib import Path
from decouple import config
from datetime import timedelta

# ==========================================
# BASE DIRECTORY
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# SECURITY
# ==========================================

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

# ==========================================
# INSTALLED APPS
# ==========================================

INSTALLED_APPS = [

    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party Apps
    'rest_framework',
    'rest_framework_simplejwt',

    # Project Apps
    'apps.accounts',
    'apps.employees',
    'apps.documents',
    'apps.payslips',
    'apps.leave',
    'apps.dashboard',
    'apps.reports',

    # Client Modules
    'resignation',
    'appraisal',
    'promotions',
    'requestsystem',

    # API
    'api',
]

# ==========================================
# MIDDLEWARE
# ==========================================

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==========================================
# URL CONFIGURATION
# ==========================================

ROOT_URLCONF = 'config.urls'

# ==========================================
# TEMPLATES
# ==========================================

TEMPLATES = [

    {

        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [

            BASE_DIR / 'templates'

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

# ==========================================
# WSGI
# ==========================================

WSGI_APPLICATION = 'config.wsgi.application'

# ==========================================
# DATABASE
# ==========================================

DATABASES = {

    'default': {

        'ENGINE': 'django.db.backends.sqlite3',

        'NAME': BASE_DIR / 'db.sqlite3',

    }

}

# ==========================================
# CUSTOM USER MODEL
# ==========================================

AUTH_USER_MODEL = 'accounts.User'

# ==========================================
# PASSWORD VALIDATION
# ==========================================

AUTH_PASSWORD_VALIDATORS = []

# ==========================================
# INTERNATIONALIZATION
# ==========================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

# ==========================================
# STATIC FILES
# ==========================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [

    BASE_DIR / 'static',

]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# ==========================================
# MEDIA FILES
# ==========================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

# ==========================================
# LOGIN / LOGOUT
# ==========================================

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/login/'

# ==========================================
# DEFAULT PRIMARY KEY
# ==========================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# DJANGO REST FRAMEWORK
# ==========================================

REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': (

        'rest_framework_simplejwt.authentication.JWTAuthentication',

    ),

    'DEFAULT_PERMISSION_CLASSES': (

        'rest_framework.permissions.IsAuthenticated',

    ),

}

# ==========================================
# JWT CONFIGURATION
# ==========================================

SIMPLE_JWT = {

    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=60
    ),

    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=7
    ),

    'ROTATE_REFRESH_TOKENS': False,

    'BLACKLIST_AFTER_ROTATION': False,

    'AUTH_HEADER_TYPES': (

        'Bearer',

    ),

}