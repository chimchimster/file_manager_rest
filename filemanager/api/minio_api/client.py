import os
import configparser

from django.conf import settings
from filemanager.settings.prod import DEBUG
from minio import Minio


MODE = bool(int(DEBUG))


def get_minio_client() -> Minio:

    if MODE:
        config = configparser.ConfigParser()
        config.read(settings.BASE_DIR / 'conf.ini')
        minio_host = config['MinIO']['HostURL']
        access_key = config['MinIO']['AccessKey']
        secret_key = config['MinIO']['SecretKey']
    else:
        minio_host = os.getenv('HOST')
        access_key = os.getenv('ACCESS_KEY')
        secret_key = os.getenv('SECRET_KEY')

    return Minio(endpoint=minio_host, access_key=access_key, secret_key=secret_key)
