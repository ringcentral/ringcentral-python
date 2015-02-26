# !/usr/bin/env python
# encoding: utf-8
import json
import re

from .headers import *


BOUNDARY_SEPARATOR = '--'
BODY_SEPARATOR = "\n\n"
UNAUTHORIZED_STATUS = 401


class Response(Headers):

    def __init__(self, status, raw, headers=None):
        Headers.__init__(self)

        self.__body = ''
        self.__raw = raw.replace('\r', '')
        self.__raw_headers = ''
        self.__data = None
        self.__status = status
        self.__responses = []

        if status is None:
            raise Exception('Empty status was received')

        if isinstance(headers, dict):
            self.set_headers(headers)
            self.__body = raw
            self.__parse_headers()

        elif self.__raw.find(BODY_SEPARATOR) > 0:
            self.__raw_headers, self.__body = self.__raw.split(BODY_SEPARATOR, 1)

        else:
            self.__body = self.__raw

        self.__parse_body()

    def check_status(self):
        return 200 <= self.__status < 300

    def get_body(self):
        return self.__body

    def get_data(self):
        return self.__data

    def get_raw(self):
        return self.__raw

    def get_status(self):
        return self.__status

    def get_responses(self):
        return self.__responses

    def __parse_headers(self):
        headers = self.__raw_headers.split('\n')
        for h in filter(lambda x: x.find(HEADER_SEPARATOR) >= 0, headers):
            k, v = h.split(HEADER_SEPARATOR, 1)
            self.set_header(k.strip(), v.strip())

    def __parse_body(self):
        if self.is_multipart():
            boundary = re.search('boundary=([^;]+)', self.get_content_type(), re.I).group(1)
            parts = self.__body.split(BOUNDARY_SEPARATOR + boundary)

            if parts[0].strip() == '':
                parts = parts[1:]
            if parts[-1].strip() == BOUNDARY_SEPARATOR:
                parts = parts[:-1]

            status_info = Response(self.__status, parts[0])

            for i, p in enumerate(parts[1:]):
                i_stat = status_info.get_data().get('response')[i].get('status')
                self.__responses.append(Response(i_stat, p))

        elif self.is_json():
            self.__data = json.loads(self.__body)
        else:
            self.__data = self.__body
