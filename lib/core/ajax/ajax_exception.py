#!/usr/bin/env python
# encoding: utf-8


class AjaxException(Exception):
    def __init__(self, ajax, prev_exception=None):
        self.__ajax = ajax
        data = ajax.get_response().get_data()
        message = ''

        if 'message' in data:
            message = data['message']
        elif 'error_description' in data:
            message = data['error_description']
        elif 'description' in data:
            message = data['description']

        if prev_exception:
            message = str(prev_exception)

        message = message or 'Unknown error'

        Exception.__init__(self, ajax.get_response().get_status(), message)

    def get_ajax(self):
        return self.__ajax