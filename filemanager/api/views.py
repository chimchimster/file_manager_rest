from django.http import Http404
from django.db.models import Prefetch

from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FileSerializer
from .models import UserFile


class ShowUserFilesDetail(APIView):

    def get(self, request) -> Response:

        user_id = request.GET.get('user')

        user_files = UserFile.objects.filter(user_id=user_id)

        serializer = FileSerializer(user_files, many=True)

        try:
            return Response({'user_id': user_id, 'files': serializer.data})
        except UserFile.DoesNotExist:
            raise Http404

