from django.contrib import admin
from .models import Storage, UserFile


@admin.register(Storage)
class StorageFileAdmin(admin.ModelAdmin):

    # Displaying
    list_display = ['file_id', 'colored_filename', 'service_name', 'status', 'created_at', 'updated_at', 'download_file']
    list_display_links = ['colored_filename']

    # Edit
    list_editable = ['status']

    # Filtering
    list_filter = ['status', 'created_at', 'updated_at', 'file_extension']

    # Searching
    search_fields = ['file_uuid', 'file_extension', 'status', 'service_name']
    search_help_text = 'Поиск по uuid, расширению, статусу и имени сервиса.'

    # Other
    date_hierarchy = 'created_at'
    show_facets = admin.ShowFacets.ALWAYS
    show_full_result_count = True
    save_on_top = True

    class Media:
        js = (
            'js/download_file.js',
        )


@admin.register(UserFile)
class UserFileAdmin(admin.ModelAdmin):

    # Displaying
    list_display = ['file_id', 'user_id']
    list_select_related = True
    list_display_links = ['file_id']

    # Searching
    search_fields = ['user_id', 'file_id__file_uuid', 'file_id__file_extension', 'file_id__status', 'file_id__service_name']
    search_help_text = 'Поиск всех связных файлов по id пользователя, uuid, расширению, статусу и имени сервиса. '\
                       'Регистр при поиске не учитывается.'

    # Filtering
    list_filter = ['file_id__status', 'file_id__created_at', 'file_id__updated_at', 'file_id__service_name']
