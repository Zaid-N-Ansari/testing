from pathlib import Path
from os.path import join

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-ni_4^q69elzvs9s$pgj!ob-l0r$1jh--@0ikiazlxf#fkb+3s0'

DEBUG = True

AUTH_USER_MODEL = 'account.UserAccount'

ALLOWED_HOSTS = []

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'account.backends.EmailOrUsernameBackend'
]

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'account:logout'
LOGIN_URL = 'account:login'
LOGOUT_URL = 'account:logout'

INSTALLED_APPS = [
	'daphne',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
	'channels',

	'app',
    'account',
	'friend',
	'chat',
]

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django.middleware.gzip.GZipMiddleware',
]

ROOT_URLCONF = 'ChatApp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'ChatApp.wsgi.application'
ASGI_APPLICATION = 'ChatApp.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

STATICFILES_DIRS = [
    join(BASE_DIR, 'static'),
    join(BASE_DIR, 'media')
]

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = join(BASE_DIR, 'static_cdn')
MEDIA_ROOT = join(BASE_DIR, 'media_cdn')

BASE_URL = 'http://127.0.0.1:8000'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
