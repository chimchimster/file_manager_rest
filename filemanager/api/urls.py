from django.urls import path

from .views import ShowUserFilesDetail

app_name = 'api'

urlpatterns = [
    path('files/', ShowUserFilesDetail.as_view(), name='user-files'),
]