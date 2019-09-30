from tornado.httputil import HTTPServerRequest


def query_argument_contains_string(request: HTTPServerRequest, query_argument_name: str, containing_value: str) -> bool:
    return containing_value in str(request.query_arguments[query_argument_name][0])
