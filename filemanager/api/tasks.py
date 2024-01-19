import io
import os
import configparser

import celery
from celery import shared_task
from django.conf import settings
from django.db import transaction
import minio.error

from api.minio_api import get_minio_client
from .models import Storage


MODE = settings.DEBUG
print("DEBUG MODE: ", MODE)
if MODE:
    config = configparser.ConfigParser()
    config.read(settings.BASE_DIR / 'conf.ini')
    BUCKET_NAME = config['MinIO']['BucketName']
else:
    BUCKET_NAME = os.getenv('BUCKET_NAME')


class CeleryTask(celery.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if isinstance(exc, ValueError):
            raise ValueError

    def run(self, *args, **kwargs):
        pass


@shared_task(base=CeleryTask)
def send_file_to_storage(file_data: bytes, file_uuid: str, file_extension: str, retries: int = 0):

    if retries > 2:
        return

    minio_client = get_minio_client()

    if minio_client.bucket_exists(BUCKET_NAME):
        with transaction.atomic():
            try:
                storage_obj = Storage.objects.get(
                    file_uuid__iexact=file_uuid,
                    file_extension__iexact=file_extension,
                )
            except Storage.DoesNotExist:
                storage_obj.status = 'E'
                storage_obj.save()
                return
            else:
                try:
                    bts = io.BytesIO(file_data)
                    minio_client.put_object(BUCKET_NAME, file_uuid + file_extension, bts, len(file_data))
                except (minio.error.MinioException, ValueError):
                    storage_obj.status = 'E'
                else:
                    storage_obj.status = 'R'
                finally:
                    storage_obj.save()
    else:
        minio_client.make_bucket(BUCKET_NAME)
        send_file_to_storage(file_data, file_uuid, file_extension, retries + 1)


@shared_task(base=CeleryTask)
def remove_file_from_storage(file_uuid: str, file_extension: str, retries: int = 0):

    if retries > 2:
        return

    minio_client = get_minio_client()

    if minio_client.bucket_exists(bucket_name):

        try:
            minio_client.remove_object(bucket_name, file_uuid + file_extension)
        except minio.error.MinioException:
            remove_file_from_storage(bucket_name, file_uuid + file_extension, retries + 1)