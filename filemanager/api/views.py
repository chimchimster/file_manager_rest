from typing import Optional

from django.db.models import Count, Q
from django.http import Http404
from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FileSerializer
from .models import UserFile, Storage
from .utils import ReqFilter
from .tasks import send_file_to_storage


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

        try:
            return Response({'user_id': user_id, 'files': serializer.data})
        except UserFile.DoesNotExist:
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
            pdf_count=Count('file_id', filter=Q(file_id__file_extension__iexact='.pdf')),
            docx_count=Count('file_id', filter=Q(file_id__file_extension__iexact='.docx')),
            pptx_count=Count('file_id', filter=Q(file_id__file_extension__iexact='.pptx')),
        )
        try:
            return Response({
                'user_id': user_id,
                'total_files': user_files_count.get('total_count', 0),
                'pdf_files': user_files_count.get('pdf_count', 0),
                'docx_files': user_files_count.get('docx_count', 0),
                'pptx_files': user_files_count.get('pptx_count', 0),
            })
        except UserFile.DoesNotExist:
            raise Http404


class UploadUserFileDetail(APIView):

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

        storage_object = Storage.objects.create(
            file_uuid=file_name,
            file_extension=file_extension,
            service_name=from_service,
            status='P',
        )

        user_file = UserFile.objects.create(
            user_id=user_id,
            file_id=storage_object,
        )

        status = send_file_to_storage(request.body, file_name, file_extension)

        if status.name == 'READY':
            user_file.status = 'R'
            user_file.save()
            return Response({'detail': 'Successfully uploaded file %s%s for user with id %s' % (file_name, file_extension, user_id)})

        user_file.status = 'E'
        user_file.save()

        return Response({'detail': 'Error occured while uploading file.'})

    @staticmethod
    def check_file_extensions(ext: str) -> Optional[Response]:

        if not ext.startswith('.'):
            return Response({'detail': 'File extension must start with point/full stop.'})

        if ext not in settings.ALLOWED_FILE_EXTENSIONS:
            return Response({'detail': 'File extension must belong allowed collection: %s' % settings.ALLOWED_FILE_EXTENSIONS})


