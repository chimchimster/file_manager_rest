from rest_framework import permissions

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view


def show_user_files_detail_swagger_schema():

    return swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'user',
                openapi.IN_QUERY,
                description='Идентификатор пользователя файлы которого Вы хотите получить.',
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                'file_uuid',
                openapi.IN_QUERY,
                description='Идентификатор файла. Идентификатор должен передан как строка состоящая из валидного типа uuid.',
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
            ),
            openapi.Parameter(
                'file_extension',
                openapi.IN_QUERY,
                description='Перед расширением файла необходимо поставить символ точки (.).',
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description='Статусы расшифровываются как ready, error, in progress соответственно.',
                type=openapi.TYPE_STRING,
                enum=['R', 'E', 'P'],
            ),
            openapi.Parameter(
                'service_name',
                openapi.IN_QUERY,
                description='Имя сервиса из которого файл был отправлен.',
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'start',
                openapi.IN_QUERY,
                description='Начальная дата поиска. Дата должна быть записана в формате: YYYY-MM-DD либо YYYY-MM-DD HH:MM:SS.',
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'end',
                openapi.IN_QUERY,
                description='Конечная дата поиска. Дата должна быть записана в формате: YYYY-MM-DD либо YYYY-MM-DD HH:MM:SS.',
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description='Номер страницы.',
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description='Количество записей для отображения на странице. Максимальное значение MaxPageSize устанавливается в filemanager/conf.ini.',
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )


def show_storage_object_detail_swagger_schema():
    return swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'file_uuid',
                openapi.IN_QUERY,
                description='Идентификатор файла. Идентификатор должен передан как строка состоящая из валидного типа uuid.',
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=True,
            ),
            openapi.Parameter(
                'start',
                openapi.IN_QUERY,
                description='Начальная дата поиска. Дата должна быть записана в формате: YYYY-MM-DD либо YYYY-MM-DD HH:MM:SS.',
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'end',
                openapi.IN_QUERY,
                description='Конечная дата поиска. Дата должна быть записана в формате: YYYY-MM-DD либо YYYY-MM-DD HH:MM:SS.',
                type=openapi.TYPE_STRING,
            ),
        ]
    )


def show_user_files_summary_detail_swagger_schema():
    return swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'user',
                openapi.IN_QUERY,
                description='Идентификатор пользователя файлы которого Вы хотите получить.',
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ]
    )


def upload_file_swagger_schema():
    return swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'from_service': openapi.Schema(type=openapi.TYPE_STRING),
                'file_uuid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                'file_extension': openapi.Schema(type=openapi.TYPE_STRING),
                'body': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['user_id', 'from_service', 'file_uuid', 'file_extension'],
        )
    )


def download_file_swagger_schema():
    return swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'file_uuid',
                openapi.IN_QUERY,
                description='Идентификатор файла. Идентификатор должен передан как строка состоящая из валидного типа uuid.',
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=True,
            ),
        ]
    )


schema_view = get_schema_view(
   openapi.Info(
      title="API файлового хранилища",
      default_version='v1',
      description="Доступ и загрузка пользовательских файлов в системе iMAS.",
      contact=openapi.Contact(email="info@imas.kz"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


__all__ = (
    'show_user_files_detail_swagger_schema',
    'show_storage_object_detail_swagger_schema',
    'show_user_files_summary_detail_swagger_schema',
    'upload_file_swagger_schema',
    'download_file_swagger_schema',
    'schema_view',
)