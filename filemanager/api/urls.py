from django.urls import path

from .views import ShowUserFilesDetail, ShowUserFilesSummaryDetail

app_name = 'api'

urlpatterns = [
    path('files/', ShowUserFilesDetail.as_view(), name='user-files'),
    path('files/summary/', ShowUserFilesSummaryDetail.as_view(), name='user-files-summary'),
]