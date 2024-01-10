import random

from django.test import TestCase, Client
from django.conf import settings
from .models import Storage, UserFile


class StorageTestCase(TestCase):

    def setUp(self):

        self.client = Client()

        api_route = '/api/v1/'
        self.files_GET = api_route + 'files/'
        self.files_file_GET = api_route + 'files/file/'
        self.files_summary_GET = api_route + 'files/summary/'
        self.files_file_download_GET = api_route + 'files/file/download/'
        self.files_file_upload_PUT = api_route + 'files/file/upload/'

        self.currently_stored_objects_mapped_to_user = dict()
        for file_name, file_extension, service_name in self.__generate_storage_data():
            storage_obj = Storage.objects.create(
                file_uuid=file_name,
                file_extension=file_extension,
                service_name=service_name,
            )

            user_id = next(self.__generate_user_id())

            if user_id not in self.currently_stored_objects_mapped_to_user:
                self.currently_stored_objects_mapped_to_user[user_id] = [storage_obj]
            else:
                self.currently_stored_objects_mapped_to_user[user_id].append(storage_obj)

            UserFile.objects.create(
                user_id=user_id,
                file_id=storage_obj,
            )

        self.registered_users = self.currently_stored_objects_mapped_to_user.keys()
        self.non_existent_users = [u_id for u_id in range(max(self.registered_users) + 1, max(self.registered_users) * 2)]

    @staticmethod
    def __generate_uuid():
        import uuid
        return uuid.uuid4()

    @staticmethod
    def __generate_extension():
        available_extensions = ('.pdf', '.docx', '.pptx', '.csv')

        return random.choice(available_extensions)

    @staticmethod
    def __generate_service_name():

        available_service_names = ('export', 'mail')

        return random.choice(available_service_names)

    @staticmethod
    def __generate_user_id():
        yield random.randint(0, 150)

    def __generate_storage_data(self):

        for _ in range(1000):
            yield self.__generate_uuid(), self.__generate_extension(), self.__generate_service_name()

    def test001_show_all_user_files_detail(self):

        for user in self.registered_users:

            # TESTING WITHOUT FILTERS

            response = self.client.get(self.files_GET, {'user': user})

            self.assertEqual(
                response.status_code,
                200,
                msg='Status code must be 200, got %s' % response.status_code,
            )

            resp_dict = response.json()

            self.assertEqual(
                len(
                    self.currently_stored_objects_mapped_to_user[
                        int(resp_dict.get('user_id'))
                    ]
                ),
                len(
                    resp_dict.get('files')
                ),
                msg='User with id %s contains wrong Storage objects' % resp_dict.get('user_id'),
            )

            # TESTING FILTERS

            # By file extension and service_name
            self.__cover_test_filters(user, file_extension=True, service_name=True)
            self.__cover_test_filters(user, file_extension=True, service_name=False)
            self.__cover_test_filters(user, file_extension=False, service_name=True)
            self.__cover_test_filters(user, file_extension=False, service_name=False)

        for non_existent_user in self.non_existent_users:
            response = self.client.get(self.files_GET, {'user': non_existent_user})

            self.assertEqual(
                response.status_code,
                404,
                msg='Status code must be 404, got %s' % response.status_code,
            )

    def __cover_test_filters(
            self,
            /,
            user_id: int,
            *,
            file_extension: bool,
            service_name: bool,
    ):
        filters = dict()

        if file_extension:
            filters.update({'file_extension': self.__generate_extension()})
        if service_name:
            filters.update({'service_name': self.__generate_service_name()})

        response = self.client.get(self.files_GET, {'user': user_id, **filters})

        resp_dict = response.json()

        if has_data := resp_dict.get('files'):
            self.assertIn(
                has_data[-1].get('file_data').get('file_id'),
                [
                    storage_obj.file_id for storage_obj
                    in self.currently_stored_objects_mapped_to_user[int(resp_dict.get('user_id'))]
                ]
            )

    def test002_show_particular_file_detail(self):

        for storage_objects in self.currently_stored_objects_mapped_to_user.values():

            for storage_object in storage_objects:
                response = self.client.get(self.files_file_GET, {'file_uuid': storage_object.file_uuid})
                self.assertEqual(
                    response.status_code,
                    200,
                    msg='Status code must be 200, got %s' % response.status_code,
                )

    def test003_show_file_summary(self):

        for user in self.registered_users:

            response = self.client.get(self.files_summary_GET, {'user': user})
            self.assertEqual(
                response.status_code,
                200,
                msg='Status code must be 200, got %s' % response.status_code,
            )

        for non_existent_user in self.non_existent_users:

            response = self.client.get(self.files_summary_GET, {'user': non_existent_user})
            self.assertEqual(
                response.status_code,
                404,
                msg='Status code must be 404, got %s' % response.status_code,
            )

