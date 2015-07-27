#!/usr/bin/env python
# encoding: utf-8


class Mocks:
    def __init__(self):
        self.__responses = []
        pass

    def add(self, mock):
        self.__responses.append(mock)
        return self

    def find(self, request):
        def finder(result, mock):
            if mock.test(request):
                result = mock
            return result

        return reduce(finder, self.__responses, None)

    def clear(self):
        self.__responses = []
        return self