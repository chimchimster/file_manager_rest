from .models import Storage, UserStorage


class DeleteFileMixin:

    @staticmethod
    def _check_for_files_availability(storage_object: Storage):

        file_id = storage_object.file_id

        availabilities = UserFile.objects.filter(file_id=file_id).values_list('available').all()

        if not all([item[-1] for item in availabilities]):
            return False
        return True