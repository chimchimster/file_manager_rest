from .utils import ParamsChecker


def validate_http_get_params(get_response):

    params_checker = ParamsChecker()

    def middleware(self, *args, **kwargs):

        nonlocal params_checker

        for key, value in self.request.GET.items():
            params_checker(key, value)

        response = get_response(self, *args, **kwargs)

        return response

    return middleware