from django.contrib import admin
from .models import Storage, UserFile


@admin.register(Storage)
class StorageFileAdmin(admin.ModelAdmin):

    list_display = ['file_id', 'file_uuid', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    list_editable = ['status']


@admin.register(UserFile)
class UserFileAdmin(admin.ModelAdmin):

    list_display = ['user_id', 'file_id']
