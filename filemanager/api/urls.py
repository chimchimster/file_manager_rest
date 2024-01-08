from django.urls import path

from .views import ShowUserFilesDetail, ShowUserFilesSummaryDetail, UploadUserFileDetail

app_name = 'api'

urlpatterns = [
    path('files/', ShowUserFilesDetail.as_view(), name='user-files'),
    path('files/summary/', ShowUserFilesSummaryDetail.as_view(), name='user-files-summary'),
    path('files/upload/<int:user_id>/<str:from_service>/<str:file_name>/<str:file_extension>/', UploadUserFileDetail.as_view(), name='user-files-upload'),
]