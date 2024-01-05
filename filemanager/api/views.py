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

        user_files_count = UserFile.objects.filter(user_id=user_id).aggregate(Count('file_id'))

        try:
            return Response({'user_id': user_id, 'total_files_count': user_files_count.get('file_id__count', 0)})
        except UserFile.DoesNotExist:
            raise Http404