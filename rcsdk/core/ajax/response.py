#!/usr/bin/env python
# encoding: utf-8
import json
import re

from .headers import *


BOUNDARY_SEPARATOR = '--'
BODY_SEPARATOR = "\n\n"
UNAUTHORIZED_STATUS = 401

class Response(Headers):

    def __init__(self, status, headers, body):
        Headers.__init__(self)
        self.__status = status
        self.__body = body
        self.set_headers(headers)
        if self.is_json():
            self.__data = json.loads(body)
        elif self.is_multipart():
            pass
        else:
            self.__data = body
        pass

    def check_status(self):
        return 200 <= self.__status < 300

    def get_body(self):
        return self.__body

    def get_data(self):
        return self.__data

    def get_status(self):
        return self.__status

