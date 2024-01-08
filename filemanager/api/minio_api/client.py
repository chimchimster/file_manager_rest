import configparser

from django.conf import settings

from minio import Minio


def get_minio_client() -> Minio:

    config = configparser.ConfigParser()
    config.read(settings.BASE_DIR / 'conf.ini')
    minio_host = config['MinIO']['HostURL']
    access_key = config['MinIO']['AccessKey']
    secret_key = config['MinIO']['SecretKey']

    return Minio(endpoint=minio_host, access_key=access_key, secret_key=secret_key)
