import io
import configparser

from celery import shared_task
from django.conf import settings
from django.db import transaction
import minio.error

from api.minio_api import get_minio_client
from .models import Storage

config = configparser.ConfigParser()
config.read(settings.BASE_DIR / 'conf.ini')
bucket_name = config['MinIO']['BucketName']


@shared_task
def send_file_to_storage(file_data: bytes, file_name: str, file_extension: str, retries: int = 0):

    if retries > 2:
        return

    minio_client = get_minio_client()

    if minio_client.bucket_exists(bucket_name):
        with transaction.atomic():
            try:
                storage_obj = Storage.objects.get(
                    file_uuid__iexact=file_name,
                    file_extension__iexact=file_extension,
                )
            except Storage.DoesNotExist:
                storage_obj.status = 'E'
                storage_obj.save()
                return
            else:
                try:
                    bts = io.BytesIO(file_data)
                    minio_client.put_object(bucket_name, file_name + file_extension, bts, -1)
                except minio.error.MinioException:
                    storage_obj.status = 'E'
                else:
                    storage_obj.status = 'R'
                finally:
                    storage_obj.save()
    else:
        minio_client.make_bucket(bucket_name)
        send_file_to_storage(file_data, file_name, file_extension, retries + 1)
