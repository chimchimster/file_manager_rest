from typing import Optional, List

from django.http import Http404

from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FileSerializer
from .models import UserFile


class ShowUserFilesDetail(APIView):

    def get(self, request) -> Response:

        user_id = request.GET.get('user')

        if user_id is None:
            raise Http404

        common_filter_names = (
            'file_extension',
            'file_uuid',
            'status',
        )

        common_filters = dict(
            map(
                lambda common_filter_list: ('file_id__' + common_filter_list[0], common_filter_list[-1]),
                filter(
                    lambda value: value is not None,
                    (self.get_not_none_filter(request, filter_name) for filter_name in common_filter_names)
                )
            )
        )

        timed_filter_names = (
            'start',
            'end',
        )

        timed_filters = dict()
        for timed_filter_name in timed_filter_names:
            if timed_filter_list := self.get_not_none_filter(request, timed_filter_name):
                operator = '__gte' if timed_filter_name == 'start' else '__lte'
                timed_filters[f'file_id__created_at{operator}'] = timed_filter_list[-1]

        page = int(request.GET.get('page', 1))
        page_size = min(abs(int(request.GET.get('page_size', 20))), 20)

        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        user_files = UserFile.objects.filter(
            user_id=user_id,
            **common_filters,
            **timed_filters,
        )[start_index:end_index]

        serializer = FileSerializer(user_files, many=True)

        try:
            return Response({'user_id': user_id, 'files': serializer.data})
        except UserFile.DoesNotExist:
            raise Http404

    @staticmethod
    def get_not_none_filter(request, filter_name: str) -> Optional[List]:

        if filter_value := request.GET.get(filter_name):
            return [filter_name, filter_value]
        return None