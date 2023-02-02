"""OpenAPI core contrib django responses module"""
from itertools import tee
from typing import Union

from django.http.response import HttpResponse
from django.http.response import StreamingHttpResponse
from werkzeug.datastructures import Headers

DjangoResponse = Union[HttpResponse, StreamingHttpResponse]


class DjangoOpenAPIResponse:
    def __init__(self, response: DjangoResponse):
        if not isinstance(response, (HttpResponse, StreamingHttpResponse)):
            raise TypeError(
                f"'response' argument is not type of (Streaming)HttpResponse"
            )
        self.response = response

    @property
    def data(self) -> str:
        if isinstance(self.response, StreamingHttpResponse):
            _, response_iterator = tee(self.response._iterator)
            content = b"".join(
                map(self.response.make_bytes, response_iterator)
            )
            return content.decode("utf-8")

        assert isinstance(self.response.content, bytes)
        return self.response.content.decode("utf-8")

    @property
    def status_code(self) -> int:
        assert isinstance(self.response.status_code, int)
        return self.response.status_code

    @property
    def headers(self) -> Headers:
        return Headers(self.response.headers.items())

    @property
    def mimetype(self) -> str:
        content_type = self.response.get("Content-Type", "")
        assert isinstance(content_type, str)
        return content_type
