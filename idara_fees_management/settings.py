





"""
Django settings for idara_fees_management project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = 'django-insecure-%eo67sj)r484)g=4l^j33-gsrdc)37^vw@i!be(z@x$+e5-&2n'
DEBUG = True
ALLOWED_HOSTS = ['idara-fees-management.onrender.com', '127.0.0.1', 'localhost']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fees_collection',
    'leave_management',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # <-- ADD THIS (important: after SessionMiddleware, before CommonMiddleware)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'idara_fees_management.urls'

# Internationalization - FIXED (removed duplicates)
LANGUAGE_CODE = 'en'  # Default language
TIME_ZONE = 'Asia/Karachi'  # Pakistan time
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Languages we support
LANGUAGES = [
    ('en', 'English'),
    ('ur', 'اردو'),  # Urdu
]

# Where translation files are stored
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Language cookie settings
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 31536000  # 1 year in seconds

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Add templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',  # <-- ADD THIS for LANGUAGES in templates
            ],
        },
    },
]

WSGI_APPLICATION = 'idara_fees_management.wsgi.application'

# Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'neondb',
        'USER': 'neondb_owner',
        'PASSWORD': 'npg_dhgOTZwFu2t9',
        'HOST': 'ep-fancy-band-a8ebbmv1-pooler.eastus2.azure.neon.tech',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Additional settings for large uploads
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 50
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 50
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000