from rest_framework import serializers

from .models import Storage, UserFile


class StorageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Storage
        fields = ['file_id', 'file_uuid', 'file_extension', 'status', 'created_at']

    def to_representation(self, instance):

        representation = super().to_representation(instance)

        current_status = representation.get('status', 'P')

        match current_status:
            case 'P':
                representation['status'] = 'In progress'
            case 'R':
                representation['status'] = 'Ready'
            case 'E':
                representation['status'] = 'Error'

        return representation


class FileSerializer(serializers.ModelSerializer):

    file_data = StorageSerializer(source='file_id', read_only=True)
    filename = serializers.SerializerMethodField()

    class Meta:
        model = UserFile
        fields = ['file_data', 'filename']

    def get_filename(self, obj):
        return '%s_%s%s' % (
            obj.file_id.file_name,
            obj.file_id.created_at.strftime('%Y-%m-%d_%H-%M'),
            obj.file_id.file_extension
        )