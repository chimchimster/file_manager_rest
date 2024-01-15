from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.urls import reverse


class Storage(models.Model):
    STATUSES = ('R', 'ready'), ('E', 'error'), ('P', 'In progress')

    file_id = models.AutoField(primary_key=True, db_column='pk')
    file_uuid = models.UUIDField(null=False, db_index=True, unique=True)
    file_extension = models.TextField(null=False)
    service_name = models.TextField(null=False)
    status = models.CharField(max_length=1, choices=STATUSES, default='P')
    created_at = models.DateTimeField(default=now, db_index=True)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return 'File №%s. Format %s' % (self.file_id, self.file_extension)

    class Meta:
        index_together = ('file_uuid', 'file_extension')

    @admin.display(description='Файл')
    def colored_filename(self):
        return format_html(
            '<span style="color: #000000;" onmouseover="this.style.color=\'#0046ff\'" onmouseout="this.style.color=\'#000000\'">{}</span>',
            '%s%s' % (self.file_uuid, self.file_extension),
        )

    @admin.display(description='Скачать файлы')
    def download_file(self):
        if self.status == 'R':
            return format_html(
                '<input class="default" type="button" name="download_file" value="Скачать файл" '
                'onclick="'
                f'let endpoint = \'{self.__form_url_to_download_file(self.file_uuid)}\';'
                'fetch(endpoint)'
                '.then(response => response.json())'
                '.then(data => downloadFile(data.file_data, data.file_name));">',
                self.__form_url_to_download_file(self.file_uuid),
            )

    @staticmethod
    def __form_url_to_download_file(file_uuid):
        return settings.REST_URL + reverse('api:download-user-file') + '?file_uuid=%s' % file_uuid


class UserFile(models.Model):
    user_id = models.IntegerField()
    file_id = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='userfiles')

    def __str__(self):
        return 'User %s, %s' % (self.user_id, self.file_id)
