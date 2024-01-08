import io
import configparser

import minio.error
from celery import shared_task
from django.conf import settings

from api.minio_api import get_minio_client, FileStatuses


config = configparser.ConfigParser()
config.read(settings.BASE_DIR / 'conf.ini')
bucket_name = config['MinIO']['BucketName']


@shared_task
def send_file_to_storage(file_data: bytes, file_name: str, file_extension: str):

    global bucket_name

    minio_client = get_minio_client()

    if minio_client.bucket_exists(bucket_name):
        try:
            bts = io.BytesIO(file_data)
            minio_client.put_object(bucket_name, file_name + file_extension, bts, 3)
        except minio.error.MinioException:
            return FileStatuses.ERROR
        else:
            return FileStatuses.READY