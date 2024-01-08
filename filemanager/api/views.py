import datetime

from django.db.models import Count, Q
from django.http import Http404

from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FileSerializer
from .models import UserFile
from .utils import ReqFilter


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

        if not request_filters:
            period = 'all_time'
        else:
            from_timestamp = request_filters.get('start', datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))
            to_timestamp = request_filters.get('end', datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))
            print(from_timestamp, to_timestamp)
            if from_timestamp == to_timestamp:
                period = from_timestamp
            else:
                period = 'from %s to %s' % (from_timestamp, to_timestamp)

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
                'period': period,
            })
        except UserFile.DoesNotExist:
            raise Http404
