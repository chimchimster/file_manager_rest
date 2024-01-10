import configparser
from typing import Optional

from django.http import Http404
from django.conf import settings
from django.db.models import Count, Q
from django.db import transaction, Error

from rest_framework.response import Response
from rest_framework.views import APIView

from .minio_api import get_minio_client

from .utils import ReqFilter
from .models import UserFile, Storage
from .exceptions import InappropriateFileStatus
from .serializers import FileSerializer, StorageSerializer

from .tasks import send_file_to_storage


config = configparser.ConfigParser()
config.read(settings.BASE_DIR / 'conf.ini')
bucket_name = config['MinIO']['BucketName']


class ShowUserFilesDetail(APIView):

    def get(self, request) -> Response:

        user_id = request.GET.get('user')

        if user_id is None:
            raise Http404

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
            raise Http404

        return Response({'user_id': user_id, 'files': serializer.data})


class ShowStorageObjectDetail(APIView):

    def get(self, request) -> Response:

        req_f = ReqFilter(
            'GET',
            {'file_uuid'},
            request=request,
            join_to=None,
        )

        request_filters = req_f.get_filters(request)

        try:
            file_info = Storage.objects.get(**request_filters)

            serializer = StorageSerializer(file_info)

            return Response({'file_data': serializer.data})
        except Storage.DoesNotExist:
            raise Http404


class ShowUserFilesSummaryDetail(APIView):

    def get(self, request) -> Response:

        user_id = request.GET.get('user')

        if user_id is None:
            raise Http404

        req_f = ReqFilter(
            'GET',
            {'start', 'end'},
            request=request,
            join_to='file_id__',
        )

        request_filters = req_f.get_filters(request)

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
        try:
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
        except UserFile.DoesNotExist:
            raise Http404


class UploadUserFile(APIView):

    def put(
            self,
            request,
            user_id: int,
            from_service: str,
            file_name: str,
            file_extension: str,
    ) -> Response:

        if has_error := self.check_file_extensions(file_extension):
            return has_error

        with transaction.atomic():
            try:
                storage_object = Storage.objects.create(
                    file_uuid=file_name,
                    file_extension=file_extension,
                    service_name=from_service,
                )

                UserFile.objects.create(
                    user_id=user_id,
                    file_id=storage_object,
                )
            except Error as e:
                return Response({'detail': 'Could not handle operation', 'exc': str(e)})

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
            raise Http404

        try:
            storage_object = Storage.objects.get(file_uuid=file_uuid)
        except Storage.DoesNotExist:
            raise Http404
        else:
            if status := {'P': 'in progress', 'E': 'error'}.get(storage_object.status):

                raise InappropriateFileStatus(
                    'File has %s status. Only files with ready status could be downloaded.' % status
                )

            return Response({
                'file_data': self.get_file_from_bucket(storage_object),
                'file_extension': storage_object.file_extension,
            })

    @staticmethod
    def get_file_from_bucket(
            storage_object: Storage,
            retry: int = 0
    ) -> bytes:

        if retry > 2:
            raise Http404

        minio_client = get_minio_client()

        try:
            result = minio_client.get_object(
                bucket_name=bucket_name,
                object_name=str(storage_object.file_uuid) + storage_object.file_extension,
            )
            return result.read()
        except Http404:
            DownloadUserFile.get_file_from_bucket(storage_object, retry + 1)


__all__ = (
    'ShowUserFilesDetail',
    'ShowStorageObjectDetail',
    'ShowUserFilesSummaryDetail',
    'UploadUserFile',
    'DownloadUserFile',
)