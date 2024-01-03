from django.http import Http404
from django.db.models import Prefetch

from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer
from .models import UserFile, Storage


class ShowUserFilesDetail(APIView):

    def get(self, request) -> Response:

        user_id = request.GET.get('user')

        user_files = UserFile.objects.filter(user_id=user_id)
        print(user_files)
        serializer = UserSerializer(user_files, many=True)

        try:
            return Response(serializer.data)
        except UserFile.DoesNotExist:
            raise Http404
