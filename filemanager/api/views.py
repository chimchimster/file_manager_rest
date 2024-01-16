import configparser
from typing import Optional

import minio.error
from django.conf import settings
from django.db.models import Count, Q
from django.db import transaction, Error
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework.views import APIView

from .minio_api import get_minio_client

from .utils import ReqFilter
from .models import UserFile, Storage
from .exceptions import *
from .serializers import FileSerializer, StorageSerializer
from .middlewares import validate_http_get_params

from .tasks import send_file_to_storage


config = configparser.ConfigParser()
config.read(settings.BASE_DIR / 'conf.ini')
bucket_name = config['MinIO']['BucketName']


class ShowUserFilesDetail(APIView):

    @validate_http_get_params
    def get(self, request) -> Response:

        user_id = request.GET.get('user')

        if user_id is None:
            raise MissingParameter(
                400,
                'Missing parameter "user".'
            )

        req_f = ReqFilter(
            'GET',
            {'file_extension', 'file_uuid', 'status', 'service_name', 'start', 'end', 'page', 'page_size'},
            request=request,
            join_to='file_id__',
        )

        request_filters = req_f.get_filters(request)
        start_index = request_filters.pop('page')
        end_index = request_filters.pop('page_size')

        user_files = UserFile.objects.filter(
            user_id=user_id,
            **request_filters,
        )[start_index:end_index]

        serializer = FileSerializer(user_files, many=True)

        if not serializer.data:
            raise DataNotFound(
                404,
                'Requested data not found on server.'
            )

        return Response({'user_id': user_id, 'files': serializer.data})


class ShowStorageObjectDetail(APIView):

    @validate_http_get_params
    def get(self, request) -> Response:

        file_uuid = request.GET.get('file_uuid')

        if not file_uuid:
            raise MissingParameter(
                400,
                'Missing parameter "file_uuid".'
            )

        req_f = ReqFilter(
            'GET',
            {'file_uuid'},
            request=request,
            join_to=None,
        )

        request_filters = req_f.get_filters(request)

        try:
            file_info = Storage.objects.get(**request_filters)
        except Storage.DoesNotExist:
            raise ObjectIsNotFound(
                404,
                'File with uuid "%s" does not exist.' % file_uuid
            )

        serializer = StorageSerializer(file_info)

        if not serializer.data:
            raise DataNotFound(
                404,
                'Requested data not found on server.'
            )
        return Response({'file_data': serializer.data})


class ShowUserFilesSummaryDetail(APIView):

    @validate_http_get_params
    def get(self, request) -> Response:

        user_id = request.GET.get('user')

        if user_id is None:
            raise MissingParameter(
                400,
                'Missing parameter "user".'
            )

        req_f = ReqFilter(
            'GET',
            {'start', 'end'},
            request=request,
            join_to='file_id__',
        )

        request_filters = req_f.get_filters(request)

        try:
            user_files_count = UserFile.objects.filter(
                user_id=user_id,
                **request_filters,
            ).aggregate(
                total_count=Count('file_id'),
                pdf_ready=Count(
                    'file_id',
                    filter=Q(file_id__file_extension__iexact='.pdf') & Q(file_id__status__iexact='R')
                ),
                docx_ready=Count(
                    'file_id',
                    filter=Q(file_id__file_extension__iexact='.docx') & Q(file_id__status__iexact='R')
                ),
                pptx_ready=Count(
                    'file_id',
                    filter=Q(file_id__file_extension__iexact='.pptx') & Q(file_id__status__iexact='R')
                ),
                pdf_error=Count(
                    'file_id',
                    filter=Q(file_id__file_extension__iexact='.pdf') & Q(file_id__status__iexact='E')
                ),
                docx_error=Count(
                    'file_id',
                    filter=Q(file_id__file_extension__iexact='.docx') & Q(file_id__status__iexact='E')
                ),
                pptx_error=Count(
                    'file_id',
                    filter=Q(file_id__file_extension__iexact='.pptx') & Q(file_id__status__iexact='E')
                ),
                pdf_in_progress=Count(
                    'file_id',
                    filter=Q(file_id__file_extension__iexact='.pdf') & Q(file_id__status__iexact='P')
                ),
                docx_in_progress=Count(
                    'file_id',
                    filter=Q(file_id__file_extension__iexact='.docx') & Q(file_id__status__iexact='P')
                ),
                pptx_in_progress=Count(
                    'file_id',
                    filter=Q(file_id__file_extension__iexact='.pptx') & Q(file_id__status__iexact='P')
                ),
            )
            if sum(user_files_count.values()) < 1:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            raise ObjectIsNotFound(
                404,
                'User\'s files with "id" %s do not found on server.' % user_id
            )
        else:
            return Response({
                'user_id': user_id,
                **user_files_count
            })


class UploadUserFile(APIView):

    @validate_http_get_params
    def put(
            self,
            request,
            user_id: int,
            from_service: str,
            file_uuid: str,
            file_extension: str,
    ) -> Response:

        if has_error := self.check_file_extensions(file_extension):
            return has_error

        with transaction.atomic():
            try:
                storage_object = Storage.objects.create(
                    file_uuid=file_uuid,
                    file_extension=file_extension,
                    service_name=from_service,
                )

                UserFile.objects.create(
                    user_id=user_id,
                    file_id=storage_object,
                )
            except Error:
                raise DatabaseErrorUpload(
                    507,
                    'Server is unable to store the representation.'
                )

        send_file_to_storage.delay(request.body, file_uuid, file_extension)

        return Response({
            'detail': 'Uploading file %s%s for user with id %s' % (file_uuid, file_extension, user_id)
        })

    @staticmethod
    def check_file_extensions(ext: str) -> Optional[Response]:

        if not ext.startswith('.'):
            return Response({'detail': 'File extension must start with point/full stop.'})

        if ext not in settings.ALLOWED_FILE_EXTENSIONS:
            return Response({
                'detail': 'File extension must belong allowed collection: %s' % settings.ALLOWED_FILE_EXTENSIONS
            })


class DownloadUserFile(APIView):

    @validate_http_get_params
    def get(self, request):

        file_uuid = request.GET.get('file_uuid')

        if file_uuid is None:
            raise MissingParameter(
                404,
                'Missing parameter "file_uuid".'
            )

        try:
            storage_object = Storage.objects.get(file_uuid=file_uuid)
        except Storage.DoesNotExist:
            raise ObjectIsNotFound(
                404,
                'Object with uuid %s does not exist.' % file_uuid
            )
        else:
            if status := {'P': 'in progress', 'E': 'error'}.get(storage_object.status):

                raise InappropriateFileStatus(
                    404,
                    'File has %s status. Only files with ready status could be downloaded.' % status
                )

            file = self.get_file_from_bucket(storage_object)
            response = HttpResponse({
                file,
            }, content_type='application/octet-stream')

            return response

    @staticmethod
    def get_file_from_bucket(
            storage_object: Storage,
            retry: int = 0,
    ) -> bytes:

        if retry > 2:
            raise MaxRetriesExceeded(
                408,
                'Tried more then %s times to download file.' % retry
            )

        minio_client = get_minio_client()

        try:
            result = minio_client.get_object(
                bucket_name=bucket_name,
                object_name=str(storage_object.file_uuid) + storage_object.file_extension,
            )

            return result.read()
        except minio.error.MinioException:
            DownloadUserFile.get_file_from_bucket(storage_object, retry + 1)


__all__ = (
    'ShowUserFilesDetail',
    'ShowStorageObjectDetail',
    'ShowUserFilesSummaryDetail',
    'UploadUserFile',
    'DownloadUserFile',
)