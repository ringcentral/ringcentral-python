#!/usr/bin/env python
# encoding: utf-8


class HttpException(Exception):
    def __init__(self, request, response):
        self.__request = request
        self.__response = response

        status = response.get_status() if response else 500
        message = response.get_error()

        Exception.__init__(self, status, message)

    def get_request(self):
        return self.__request

    def get_response(self):
        return self.__response