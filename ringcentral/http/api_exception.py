#!/usr/bin/env python
# encoding: utf-8


class ApiException(Exception):
    def __init__(self, apiResponse, previous=None):
        self.__apiResponse = apiResponse

        message = previous.message if previous else 'Unknown error'
        status = 0  # previous.status if previous else 0

        if apiResponse:

            if apiResponse.error():
                message = apiResponse.error()

            if apiResponse.response() and apiResponse.response().status_code:
                status = apiResponse.response().status_code

        Exception.__init__(self, status, message)

    def api_response(self):
        return self.__apiResponse