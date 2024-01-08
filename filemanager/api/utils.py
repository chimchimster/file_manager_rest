import abc

from typing import Optional


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


class HttpRequestFilterABC(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def get_filter_list_or_none(request, filter_name: str) -> Optional[list[str, str]]:
        """ Based on filter name availability inside one of HTTP method
        namespace returns collection of filter name and its value. Otherwise, returns None. """

    @abc.abstractmethod
    def get_filters(self):
        """ Returns dictionary with all filters from Request. """


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
