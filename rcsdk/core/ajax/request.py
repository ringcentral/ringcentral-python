#!/usr/bin/env python
# encoding: utf-8
import json
import urllib

from .headers import *


POST = 'POST'
GET = 'GET'
DELETE = 'DELETE'
PUT = 'PUT'

ALLOWED_METHODS = [GET, POST, PUT, DELETE]


class Request(Headers):
    def __init__(self, method, url, query_params=None, body=None, headers=None):
        Headers.__init__(self)

        if method not in ALLOWED_METHODS:
            raise Exception('Unknown method')

        self.__method = method
        self.__url = url
        self.__query_params = query_params if query_params else {}
        self.__body = body

        self.set_headers({
            ACCEPT: JSON_CONTENT_TYPE,
            CONTENT_TYPE: JSON_CONTENT_TYPE
        })

        if headers:
            self.set_headers(headers)

    def get_url(self):
        return self.__url

    def get_url_with_query_string(self):
        url = self.__url
        query = urllib.urlencode(self.__query_params)
        if query:
            url = ('&' if self.__url.find('?') > 0 else '?') + query
        return url

    def get_encoded_body(self):
        if self.is_json():
            return json.dumps(self.__body)
        elif self.is_url_encoded():
            return urllib.urlencode(self.__body)
        else:
            return self.__body

    def is_put(self):
        return self.__method == PUT

    def is_get(self):
        return self.__method == GET

    def is_post(self):
        return self.__method == POST

    def is_delete(self):
        return self.__method == DELETE

    def get_method(self):
        return self.__method

    def set_method(self, method):
        self.__method = method

    def set_url(self, url):
        self.__url = url

    def get_body(self):
        return self.__body

    def set_body(self, body):
        self.__body = body

    def get_query_params(self):
        return self.__query_params
