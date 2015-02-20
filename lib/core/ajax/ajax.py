#!/usr/bin/env python
# encoding: utf-8


class Ajax:
    def __init__(self, request):
        self.__request = request
        self.__response = None

    def send(self):
        print "sdlkfjgsdfkjlgjhljgkfh!!!!"
        pass

    def is_loaded(self):
        return True if self.__response else False

    def get_response(self):
        return self.__response

    def get_request(self):
        return self.__request