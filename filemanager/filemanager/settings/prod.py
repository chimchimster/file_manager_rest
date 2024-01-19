import os

from .base import *


SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = bool(int(os.getenv('DEBUG')))

# Databases definition

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.getenv('MARIA_HOST'),
        'PORT': os.getenv('MARIA_PORT'),
        'USER': os.getenv('MARIA_DB_USER'),
        'NAME': os.getenv('MARIA_DB_NAME'),
        'PASSWORD': os.getenv('MARIA_DB_PASSWORD'),
        'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
    }
}

# Celery configuration

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')

# Filemanager (app) configuration

ALLOWED_FILE_EXTENSIONS = os.getenv('ALLOWED_FILES_EXTENSIONS').split(',')
ALLOWED_SERVICE_NAMES = os.getenv('ALLOWED_SERVICES_NAMES').split(',')

DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv('DATA_UPLOAD_MAX_MEMORY_SIZE'))

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS').split(',')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

# Common configurations

MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE'))
