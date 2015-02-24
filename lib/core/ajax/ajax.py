#!/usr/bin/env python
# encoding: utf-8

import pycurl
import StringIO

from response import *
from ajax_exception import AjaxException


class Ajax:
    def __init__(self, request):
        self.__request = request
        self.__response = None

    def send(self):
        buf = StringIO.StringIO()
        h_buf = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, self.__request.get_url_with_query_string())
        c.setopt(pycurl.HTTPHEADER, self.__request.get_headers_array())
        if self.__request.is_put() or self.__request.is_post():
            c.setopt(pycurl.POST, True)
            c.setopt(pycurl.POSTFIELDS, self.__request.get_encoded_body())
        c.setopt(pycurl.WRITEFUNCTION, buf.write)
        c.setopt(pycurl.HEADERFUNCTION, h_buf.write)
        try:
            c.perform()
            code = c.getinfo(pycurl.HTTP_CODE)
            content = buf.getvalue()
            h_content = h_buf.getvalue()
            raw = (h_content + BODY_SEPARATOR if h_content else '') + content
            self.__response = Response(code, raw)

            if not self.__response.check_status():
                raise AjaxException(self)

        except Exception, e:
            raise AjaxException(self, e)
        finally:
            c.close()

    def is_loaded(self):
        return True if self.__response else False

    def get_response(self):
        return self.__response

    def get_request(self):
        return self.__request