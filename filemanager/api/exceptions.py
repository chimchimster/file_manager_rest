from rest_framework.exceptions import APIException


class BaseAPIException(APIException):

    status_code = None
    detail = None

    def __init__(self, status_code, message):
        self.__class__.status_code = status_code
        self.__class__.detail = message


class InappropriateFileStatus(BaseAPIException):
    pass


class ObjectIsNotFound(BaseAPIException):
    pass


class FileHasBeenUnlinked(BaseAPIException):
    pass


class FileHasBeenRemovedFromBucket(BaseAPIException):
    pass


class MissingParameter(BaseAPIException):
    pass


class DataNotFound(BaseAPIException):
    pass


class DatabaseErrorUpload(BaseAPIException):
    pass


class MaxRetriesExceeded(BaseAPIException):
    pass


class WrongUserIDFormat(BaseAPIException):
    pass


class WrongUUIDFormat(BaseAPIException):
    pass


class WrongStatusFormat(BaseAPIException):
    pass


class WrongFileExtension(BaseAPIException):
    pass


class WrongPaginationValue(BaseAPIException):
    pass


class WrongService(BaseAPIException):
    pass


__all__ = [
    'InappropriateFileStatus',
    'ObjectIsNotFound',
    'MissingParameter',
    'DataNotFound',
    'DatabaseErrorUpload',
    'MaxRetriesExceeded',
    'WrongUserIDFormat',
    'WrongUUIDFormat',
    'WrongStatusFormat',
    'WrongFileExtension',
    'WrongPaginationValue',
    'WrongService',
    'FileHasBeenUnlinked',
    'FileHasBeenRemovedFromBucket',
]