import configparser

from .base import *

config = configparser.ConfigParser()
config.read(BASE_DIR / 'conf.ini')

SECRET_KEY = config['DEPLOY MODE']['SecretKey']
DEBUG = config['DEPLOY MODE']['DEBUG']

# Databases definition

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': config['MARIA DB']['MariaHost'],
        'PORT': int(config['MARIA DB']['MariaPort']),
        'USER': config['MARIA DB']['DatabaseUser'],
        'NAME': config['MARIA DB']['DatabaseName'],
        'PASSWORD': config['MARIA DB']['DatabasePassword'],
        'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
    }
}

# Celery configuration

CELERY_BROKER_URL = config['CELERY']['BROKER_URL']

# Filemanager (app) configuration

ALLOWED_FILE_EXTENSIONS = config['DEPLOY MODE']['AllowedFilesExtensions'].split('\n')
ALLOWED_SERVICE_NAMES = config['DEPLOY MODE']['AllowedServiceNames'].split('\n')

DATA_UPLOAD_MAX_MEMORY_SIZE = int(config['DEPLOY MODE']['DataUploadMaxMemorySize'])

CORS_ALLOWED_ORIGINS = config['DEPLOY MODE']['CORSAllowedOrigins'].split('\n')
ALLOWED_HOSTS = config['DEPLOY MODE']['AllowedHosts'].split('\n')

# Common configurations

MAX_PAGE_SIZE = int(config['DEPLOY MODE']['MaxPageSize'])
