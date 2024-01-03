import datetime

from rest_framework import serializers
from .models import Storage, UserFile


class StorageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Storage
        fields = ['file_uuid', 'status', 'created_at']


class UserSerializer(serializers.ModelSerializer):

    file = StorageSerializer(source='file_id')
    filename = serializers.SerializerMethodField()

    class Meta:
        model = UserFile
        fields = ['user_id', 'file', 'filename']

    def get_filename(self, obj):
        return 'iMAS %s report' % obj.file_id.created_at