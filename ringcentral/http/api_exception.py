#!/usr/bin/env python
# encoding: utf-8


class ApiException(Exception):
    def __init__(self, api_response, previous=None):
        self.__apiResponse = api_response

        message = previous.message if previous and hasattr(previous, 'message') else 'Unknown error'
        status = 0  # previous.status if previous else 0

        if api_response:

            if api_response.error():
                message = api_response.error()

            if api_response.response() and api_response.response().status_code:
                status = api_response.response().status_code

        super(ApiException, self).__init__(message)

    def api_response(self):
        return self.__apiResponse