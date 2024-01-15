import configparser
from typing import Optional

import minio.error
from django.conf import settings
from django.db.models import Count, Q
from django.db import transaction, Error
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework.views import APIView

from .minio_api import get_minio_client

from .utils import ReqFilter, ParamsChecker
from .models import UserFile, Storage
from .exceptions import *
from .serializers import FileSerializer, StorageSerializer

from .tasks import send_file_to_storage


config = configparser.ConfigParser()
config.read(settings.BASE_DIR / 'conf.ini')
bucket_name = config['MinIO']['BucketName']


class ShowUserFilesDetail(APIView):

    def get(self, request) -> Response:

        r_get = request.GET

        user_id = r_get.get('user')

        if user_id is None:
            raise MissingParameter(
                400,
                'Missing parameter "user".'
            )

        params_map = {
            'user': user_id,
            'uuid': r_get.get('file_uuid'),
            'extension': r_get.get('file_extension'),
            'status': r_get.get('status'),
            'service': r_get.get('service_name'),
        }
        params_checker = ParamsChecker()
        for name, value in params_map.items():
            if value is not None:
                params_checker(name, value)

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

    def get(self, request) -> Response:

        file_uuid = request.GET.get('file_uuid')

        if not file_uuid:
            raise MissingParameter(
                400,
                'Missing parameter "file_uuid".'
            )

        params_checker = ParamsChecker()
        params_checker('uuid', file_uuid)

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

    def get(self, request) -> Response:

        r_get = request.GET
        user_id = r_get.get('user')

        if user_id is None:
            raise MissingParameter(
                400,
                'Missing parameter "user".'
            )

        params_checker = ParamsChecker()
        params_checker('user', user_id)

        start = r_get.get('start')
        end = r_get.get('end')
        if start is not None:
            params_checker('pagination', start)
        if end is not None:
            params_checker('pagination', end)

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
                'total_files': user_files_count.get('total_count', 0),
                'pdf_ready': user_files_count.get('pdf_ready', 0),
                'docx_ready': user_files_count.get('docx_ready', 0),
                'pptx_ready': user_files_count.get('pptx_ready', 0),
                'pdf_error': user_files_count.get('pdf_error', 0),
                'docx_error': user_files_count.get('docx_error', 0),
                'pptx_error': user_files_count.get('pptx_error', 0),
                'pdf_in_progress': user_files_count.get('pdf_in_progress', 0),
                'docx_in_progress': user_files_count.get('docx_in_progress', 0),
                'pptx_in_progress': user_files_count.get('pptx_in_progress', 0),
            })


class UploadUserFile(APIView):

    def put(
            self,
            request,
            user_id: int,
            from_service: str,
            file_uuid: str,
            file_extension: str,
    ) -> Response:

        params_checker = ParamsChecker()
        params_checker('user', user_id)
        params_checker('uuid', file_uuid)
        params_checker('extension', file_extension)
        params_checker('service', from_service)

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

        send_file_to_storage.delay(request.body, file_name, file_extension)

        return Response({
            'detail': 'Uploading file %s%s for user with id %s' % (file_name, file_extension, user_id)
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

            file_name = self.__get_filename(storage_object)

            file = self.get_file_from_bucket(storage_object)

            return Response({
                'file_data': file,
                'file_name': file_name,
            })

    @staticmethod
    def __get_filename(obj):
        return '%s_%s%s' % (
            obj.service_name,
            obj.created_at.strftime('%Y-%m-%d_%H-%M'),
            obj.file_extension
        )

    @staticmethod
    def get_file_from_bucket(
            storage_object: Storage,
            retry: int = 0
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