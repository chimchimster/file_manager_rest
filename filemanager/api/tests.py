from django.test import TestCase
from .models import Storage


class StorageTestCase(TestCase):

    def setUp(self):

        for file_name, file_extension, service_name in self.__generate_storage_data():
            Storage.objects.create(
                file_uuid=file_name,
                file_extension=file_extension,
                service_name=service_name
            )

    @staticmethod
    def __generate_uuid():
        import uuid
        yield uuid.uuid4()

    @staticmethod
    def __generate_extension():
        import random
        available_extensions = ('.pdf', '.docx', '.pptx', '.csv')

        yield random.choice(available_extensions)

    @staticmethod
    def __generate_service_name():
        import random
        available_service_names = ('export', 'mail')

        yield random.choice(available_service_names)

    def __generate_storage_data(self):

        yield from self.__generate_uuid()
        yield from self.__generate_extension()
        yield from self.__generate_service_name()
