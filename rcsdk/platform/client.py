#!/usr/bin/env python
# encoding: utf-8

import base64

from ..http.request import *


class Client:
    def __init__(self, platform):
        self.__platform = platform

    def get(self, url, query_params=None, headers=None):
        return self.__platform.api_call(Request(GET, url, query_params, None, headers))

    def post(self, url, query_params=None, body=None, headers=None):
        return self.__platform.api_call(Request(POST, url, query_params, body, headers))

    def put(self, url, query_params=None, body=None, headers=None):
        return self.__platform.api_call(Request(PUT, url, query_params, body, headers))

    def delete(self, url, query_params=None, body=None, headers=None):
        return self.__platform.api_call(Request(DELETE, url, query_params, body, headers))
