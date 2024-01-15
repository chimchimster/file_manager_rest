import uuid
from typing import Optional, Any

from .exceptions import *


class HttpRequestFilter(type):

    # Common filters intended to search accurate values using Django ORM.
    # Example of usage:
    #       CustomModel.objects.filter(**{'field': value})
    #       or in more common way CustomModel.objects.filter(field=value)
    __common_filter_names = (
        'file_extension',
        'file_uuid',
        'status',
        'service_name',
    )

    # Timed filters is intended to filter records by the timestamps.
    # Example of usage:
    #       CustomModel.objects.filter(**{'field_gte', value}). Choices are gte, lte.
    # Note that If "start" equals "end" means that eq is used.
    __timed_filter_names = (
        'start',
        'end',
    )

    # Pagination filters is intended to control number of records displayed on each page.
    # Example of usage:
    #       CustomModel.objects.filter(field=value)[start_index:end_index]
    __pagination_filter_names = (
        'page',
        'page_size',
    )

    def __new__(cls, name, bases, namespace):

        available_request_params = namespace.get('_%s__available_request_params' % namespace.get('__qualname__', ''), ())

        for request_param in available_request_params:
            filter_name = f'{request_param.lower()}_filters'

            namespace[filter_name] = cls.create_filter_method(request_param)

        return super().__new__(cls, name, bases, namespace)

    @staticmethod
    def create_filter_method(request_param):
        def filter_method(self, request):

            nonlocal request_param

            if request_param == 'GET':

                cm_flt = HttpRequestFilter.__get_common_filters(self, request)
                tm_flt = HttpRequestFilter.__get_timed_filters(self, request)
                pg_flt = HttpRequestFilter.__get_pagination_filters(self, request)
                return {**cm_flt, **tm_flt, **pg_flt}

            elif request_param == 'POST':
                pass

        return filter_method

    @staticmethod
    def __get_common_filters(self, request) -> dict[str, str]:

        return dict(
            map(
                lambda common_filter_list: (
                    (self._join_to if self._join_to else '') + common_filter_list[0] + '__iexact', common_filter_list[-1]
                ),
                filter(
                    lambda value: value is not None,
                    (
                        self.get_filter_list_or_none(request, filter_name)
                        for filter_name in HttpRequestFilter.__common_filter_names if filter_name in self._allowed_filters
                    )
                )
            )
        )

    @staticmethod
    def __get_timed_filters(self, request) -> dict[str, str]:

        timed_filters = dict()
        for timed_filter_name in HttpRequestFilter.__timed_filter_names:
            if (timed_filter_name in self._allowed_filters
                    and (timed_filter_list := self.get_filter_list_or_none(request, timed_filter_name))):
                operator = '__gte' if timed_filter_name == 'start' else '__lte'
                timed_filters[
                    f'{self._join_to if self._join_to else ""}created_at{operator}'
                ] = timed_filter_list[-1]

        return timed_filters

    @staticmethod
    def __get_pagination_filters(self, request) -> dict[str, int]:

        if all(('page' in self._allowed_filters, 'page_size' in self._allowed_filters)):
            page = abs(int(request.GET.get('page', 1)))
            page_size = min(abs(int(request.GET.get('page_size', 20))), 20)

            start_index = (page - 1) * page_size
            end_index = start_index + page_size

            return {'page': start_index, 'page_size': end_index}
        return {}


class ReqFilter(metaclass=HttpRequestFilter):

    __available_request_params = ('GET', 'POST')

    def __init__(self, /, request_param: str, allowed_filters: set, *, request, join_to=None):

        assert request_param in self.__available_request_params, (
                'Unavailable request parameter. Use %s' % ', '.join(self.__available_request_params)
        )
        assert isinstance(join_to, (str | None)), 'Type of join_to parameter must be either str or None.'

        self.__req_param = request_param
        self._allowed_filters = allowed_filters
        self.__req = request
        self._join_to = join_to

    @staticmethod
    def get_filter_list_or_none(request, filter_name: str) -> Optional[list[str]]:

        if filter_value := request.GET.get(filter_name):
            return [filter_name, filter_value]
        return None

    def get_filters(self, request):

        filter_method = getattr(self, f'{self.__req_param.lower()}_filter', None)

        if filter_method:
            return filter_method(request)
        return {}


class ParamsChecker:

    __available_check_methods = {}

    def __new__(cls, *args, **kwargs):

        instance = super().__new__(cls)

        cls.__available_check_methods = {
            'user': instance.__check_user,
            'file_uuid': instance.__check_uuid,
            'status': instance.__check_status,
            'file_extension': instance.__check_extension,
            'start': instance.__check_pagination,
            'end': instance.__check_pagination,
            'service_name': instance.__check_service,
        }

        return instance

    def __call__(self, name: str, value: Any):

        check_method = self.__available_check_methods.get(name)
        if check_method is not None:
            check_method(value)
        else:
            raise ValueError('Invalid check %s' % name)

    @staticmethod
    def __check_user(value):
        try:
            u_id = int(value)
            if u_id <= 0:
                raise ValueError("User ID must be a positive integer.")
        except (TypeError, ValueError):
            raise WrongUserIDFormat(
                400,
                'Wrong user ID format.'
            )

    @staticmethod
    def __check_uuid(value):
        try:
            uuid_obj = uuid.UUID(value)
            if str(uuid_obj) != value:
                raise ValueError('String is not valid UUID.')
        except (TypeError, ValueError):
            raise WrongUserIDFormat(
                400,
                'Wrong file uuid format.'
            )

    @staticmethod
    def __check_status(value):
        if value not in ('P', 'R', 'E'):
            raise WrongStatusFormat(
                400,
                'Wrong file status format.'
            )

    @staticmethod
    def __check_extension(value):
        if value not in ('.pdf', '.docx', '.xlsx', '.csv'):
            raise WrongFileExtension(
                400,
                'Wrong file extension format.'
            )

    @staticmethod
    def __check_pagination(value):
        try:
            vl = int(value)
            if vl <= 0:
                raise ValueError('Pagination value must be positive integer.')
        except (TypeError, ValueError):
            raise WrongPaginationValue(
                400,
                'Pagination value must be positive integer.'
            )

    @staticmethod
    def __check_service(value):
        if value not in ('export', 'mail'):
            raise WrongService(
                400,
                'Uploading files from not known service is restricted.'
            )

    @staticmethod
    def __check_page(value):
        pass
