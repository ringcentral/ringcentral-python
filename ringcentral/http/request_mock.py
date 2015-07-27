#!/usr/bin/env python
# encoding: utf-8

from .request import Request
from .http_exception import HttpException


class RequestMock(Request):
    def __init__(self, mocks, method, url, query_params=None, body=None, headers=None):
        Request.__init__(self, method, url, query_params, body, headers)
        self.__mocks = mocks

    def send(self):
        mock = self.__mocks.find(self)

        if not mock:
            message = 'Mock for path "' + self.get_url() + '" was not found in contextual mocks registry'
            raise HttpException(self, None, Exception(message))

        response = mock.get_response(self)

        if not response.check_status():
            raise HttpException(self, response, Exception('Response has unsuccessful status'))

        return response