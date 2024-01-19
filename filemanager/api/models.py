import urllib.parse

from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.urls import reverse
from django.db.models import F


class Storage(models.Model):
    STATUSES = ('R', 'ready'), ('E', 'error'), ('P', 'In progress')

    file_id = models.AutoField(primary_key=True, db_column='pk')
    file_uuid = models.UUIDField(null=False, db_index=True, verbose_name='Уникальный идентификатор файла')
    file_extension = models.CharField(max_length=6, null=False, verbose_name='Расширение файла')
    service_name = models.CharField(max_length=15, null=False, verbose_name='Имя сервиса')
    status = models.CharField(max_length=1, choices=STATUSES, default='P', verbose_name='Статус готовности')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания файла')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения файла')

    def __str__(self):
        return 'Файл %s%s. Статус %s. Добавлен сервисом %s в %s' % (
            self.file_uuid,
            self.file_extension,
            self.status,
            self.service_name,
            self.created_at.strftime('%d-%B-%Y %H:%M:%S')
        )

    class Meta:
        ordering = ('-updated_at',)

        verbose_name = 'Хранилище'
        verbose_name_plural = 'Хранилище'

    @admin.display(description='Файл')
    def colored_filename(self):
        return format_html(
            '<span style="color: #000000;" onmouseover="this.style.color=\'#0046ff\'" onmouseout="this.style.color=\'#000000\'">{}</span>',
            '%s%s' % (self.file_uuid, self.file_extension),
        )

    @admin.display(description='Скачать файлы')
    def download_file(self):
        if self.status == 'R':
            filename = self._get_filename(self)
            encoded_filename = urllib.parse.quote(filename)
            return format_html(
                '<input class="default" type="button" name="download_file" value="Скачать файл" '
                'onclick="'
                f'let endpoint = \'{self.__form_url_to_download_file(self.file_uuid)}\';'
                'fetch(endpoint)'
                '.then(response => response.blob())'
                '.then(blob => downloadFile(blob, decodeURIComponent(\'%s\')));">' % encoded_filename,
                self.__form_url_to_download_file(self.file_uuid),
            )

    @staticmethod
    def _get_filename(obj):
        return '%s_%s%s' % (
            obj.service_name,
            obj.created_at.strftime('%Y-%m-%d_%H-%M'),
            obj.file_extension
        )

    @staticmethod
    def __form_url_to_download_file(file_uuid):
        return reverse('api:download-file') + '?file_uuid=%s' % file_uuid


class UserStorage(models.Model):
    user_id = models.IntegerField(verbose_name='Пользователь')
    file_id = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='userfiles', verbose_name='Файл')
    available = models.BooleanField(default=True, null=False, verbose_name='Доступно')

    def __str__(self):
        return 'Пользователь %s: %s' % (self.user_id, self.file_id)

    class Meta:
        verbose_name = 'Файл пользователя'
        verbose_name_plural = 'Файлы пользователя'
        ordering = (F('file_id__updated_at').desc(),)
        constraints = (
            models.UniqueConstraint(
                fields=['user_id', 'file_id'],
                name='unique_user__file'
            ),
        )
