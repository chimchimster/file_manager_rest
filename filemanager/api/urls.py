from django.urls import path

from .views import *
from .swagger_docs import schema_view

app_name = 'api'


urlpatterns = [

    # GET methods
    path('files/', ShowUserFilesDetail.as_view(), name='user-files'),
    path('files/file/', ShowStorageObjectDetail.as_view(), name='user-file'),
    path('files/summary/', ShowUserFilesSummaryDetail.as_view(), name='user-files-summary'),
    path('files/file/download/', DownloadUserFile.as_view(), name='download-user-file'),

    # PUT methods
    path(
        'files/file/upload/<int:user_id>/<str:from_service>/<str:file_uuid>/<str:file_extension>/',
        UploadUserFile.as_view(),
        name='user-files-upload'
    ),

    # Docs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
