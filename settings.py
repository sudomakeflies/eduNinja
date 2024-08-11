import os
import environ
from pathlib import Path

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(_file_)))
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR  = Path(__file__).resolve().parent

# Inicializar django-environ
env = environ.Env(
    DEBUG=(bool, True)
)
#environ.Env.read_env()

# Lee el archivo .env si existe
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Asigna la SECRET_KEY desde el entorno
SECRET_KEY = env('SECRET_KEY')

#Flexibiliza o relaja las restricciones de password en el registro de usuarios
AUTH_PASSWORD_VALIDATORS = []

DEBUG = env('DEBUG')

# Configura la URL para acceder a los archivos media
MEDIA_URL = '/media/'
# Configura el directorio donde se almacenarán los archivos media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Esta es la ruta donde se recopilan todos los archivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
#ASGI
ASGI_APPLICATION = 'asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis://localhost:6379')],
        },
    },
}

# Allow all origins (for testing purposes)
CORS_ALLOW_ALL_ORIGINS = True


# Antrophic KEY
ANTHROPIC_API_KEY = env('ANTHROPIC_API_KEY')

# Otros ajustes ...
LOGIN_REDIRECT_URL = 'profile'
LOGOUT_REDIRECT_URL = 'login'

# Seguridad adicional
#Daphne segurity
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
#SECURE_HSTS_SECONDS = 0  # Disable HSTS for local development

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

INSTALLED_APPS = [
    # ...
    'personalized_learning',
    'evaluations',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    #'langchain',
    #'channels',
    'corsheaders',
    'rest_framework',
    #'whitenoise.runserver_nostatic',
]


#if DEBUG:
#    INSTALLED_APPS += ['silk', 'debug_toolbar']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'evalsdb',
        'USER': 'admin',
        'PASSWORD': 'password',
        'HOST': 'db',
        'PORT': '5432',
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'whitenoise.middleware.WhiteNoiseMiddleware',
]

# Agregar middlewares adicionales si estamos en modo DEBUG
#if DEBUG:
#    MIDDLEWARE += ['silk.middleware.SilkyMiddleware', 'debug_toolbar.middleware.DebugToolbarMiddleware']


"""INTERNAL_IPS = [
    '127.0.0.1',
]"""

ROOT_URLCONF = 'urls'

WGSI_APPLICATION = 'wsgi.application'

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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django_debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'daphne': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'channels': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
#AUTH_USER_MODEL = 'personalized_learning.NinjaUser'
