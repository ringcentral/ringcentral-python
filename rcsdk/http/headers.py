#!/usr/bin/env python
# encoding: utf-8

HEADER_SEPARATOR = ':'
CONTENT_TYPE = 'content-type'
AUTHORIZATION = 'authorization'
ACCEPT = 'accept'
URL_ENCODED_CONTENT_TYPE = 'application/x-www-form-urlencoded'
JSON_CONTENT_TYPE = 'application/json'
MULTIPART_CONTENT_TYPE = 'multipart/mixed'


class Headers:
    def __init__(self):
        self.headers = {}

    def set_header(self, key, val):
        self.headers[key.lower()] = val

    def set_headers(self, headers):
        for k in headers.keys():
            self.set_header(k, headers[k])

    def get_header(self, key):
        return self.headers.get(key.lower())

    def has_header(self, key):
        return key.lower() in self.headers

    def get_headers(self):
        return self.headers

    def get_headers_array(self):
        return [k.lower() + HEADER_SEPARATOR + str(self.headers[k]) for k in self.headers.keys()]

    def get_content_type(self):
        return self.get_header(CONTENT_TYPE)

    def set_content_type(self, ct):
        self.set_header(CONTENT_TYPE, ct)

    def is_content_type(self, ct):
        return self.get_content_type().find(ct) >= 0

    def is_json(self):
        return self.is_content_type(JSON_CONTENT_TYPE)

    def is_multipart(self):
        return self.is_content_type(MULTIPART_CONTENT_TYPE)

    def is_url_encoded(self):
        return self.is_content_type(URL_ENCODED_CONTENT_TYPE)
