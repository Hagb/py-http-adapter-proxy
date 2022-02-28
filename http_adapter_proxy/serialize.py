from requests import PreparedRequest, Response
from requests.structures import CaseInsensitiveDict
from urllib3.response import HTTPResponse
def deserialize_requests_response(to_deserialize: dict, prepared_request: PreparedRequest):
    """
    Create and return a Response based on the contents of the given dictionary.
    :param to_deserialize: The dictionary to create the Response from.
    :return: A Response created by the contents of to_deserialize.
    """
    # From https://github.com/lavalamp-/ws-backend-community
    to_return = Response()
    to_return.status_code = to_deserialize["status_code"]
    to_return.headers = CaseInsensitiveDict(to_deserialize["headers"])
    to_return.encoding = to_deserialize["encoding"]
    to_return._content = to_deserialize["content"]
    to_return._content_consumed = True
    to_return.reason = to_deserialize["reason"]
    to_return.url = to_deserialize["url"]
    to_return.request = prepared_request
    to_return.raw = to_deserialize["raw"]
    return to_return

def serialize_requests_response(to_serialize: Response) -> dict:
    """
    Serialize the contents of the given requests library response object to a JSON dictionary. A response
    is populated by the requests adapter build_response method as follows:

    response = Response()
    response.status_code = getattr(resp, 'status', None)
    response.headers = CaseInsensitiveDict(getattr(resp, 'headers', {}))
    response.encoding = get_encoding_from_headers(response.headers)
    response.raw = resp
    response.reason = response.raw.reason
    if isinstance(req.url, bytes):
        response.url = req.url.decode('utf-8')
    else:
        response.url = req.url
    extract_cookies_to_jar(response.cookies, req, resp)
    response.request = req
    response.connection = self
    return response

    :param to_serialize: The response object to serialize.
    :return: A JSON object representing the contents of the given response.
    """
    raw = HTTPResponse()
    raw._original_response = to_serialize.raw._original_response
    return {
        "status_code": to_serialize.status_code,
        "headers": dict(to_serialize.headers),
        "encoding": to_serialize.encoding,
        "content": to_serialize.content,
        "reason": to_serialize.reason,
        "url": to_serialize.url,
        # "request.": to_serialize.request,
        'raw': raw
        # "request": self.encode(to_serialize.request),
        # "__class_type": get_import_path_for_type(to_serialize),
    }


def deserialize_requests_prepared_request(to_deserialize):
    """
    Create and return a PreparedRequest based on the contents of the given dictionary.
    :param to_deserialize: The dictionary to create the PreparedRequest from.
    :return: A PreparedRequest created by the contents of to_deserialize.
    """
    to_return = PreparedRequest()
    to_return.method = to_deserialize["method"]
    to_return.url = to_deserialize["url"]
    to_return.headers = to_deserialize["headers"]
    to_return.body = to_deserialize["body"]
    return to_return


def serialize_requests_prepared_request(to_serialize):
    """
    Serialize the contents of the given requests library request object to a JSON dictionary. A request is
    populated by the requests session object as follows:

    def copy(self):
        p = PreparedRequest()
        p.method = self.method
        p.url = self.url
        p.headers = self.headers.copy() if self.headers is not None else None
        p._cookies = _copy_cookie_jar(self._cookies)
        p.body = self.body
        p.hooks = self.hooks
        p._body_position = self._body_position
        return p

    :param to_serialize: The request object to serialize.
    :return: A JSON object representing the contents of the given request.
    """
    return {
        "method": to_serialize.method,
        "url": to_serialize.url,
        "headers": dict(to_serialize.headers),
        "body": to_serialize.body,
        # "__class_type": get_import_path_for_type(to_serialize),
    }