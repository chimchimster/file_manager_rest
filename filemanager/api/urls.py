from django.urls import path

from .views import *

app_name = 'api'

urlpatterns = [

    # GET methods
    path('files/', ShowUserFilesDetail.as_view(), name='user-files'),
    path('files/file/', ShowStorageObjectDetail.as_view(), name='user-file'),
    path('files/summary/', ShowUserFilesSummaryDetail.as_view(), name='user-files-summary'),

    # PUT methods
    path(
        'files/upload/<int:user_id>/<str:from_service>/<str:file_name>/<str:file_extension>/',
        UploadUserFileDetail.as_view(),
        name='user-files-upload'
    ),
]
