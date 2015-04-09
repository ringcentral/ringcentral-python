#!/usr/bin/env python
# encoding: utf-8

from .mock import *
from ..response import Response


class GenericMock(Mock):
    def __init__(self, path, body=None, status=200):
        Mock.__init__(self)

        self._path = '/restapi/v1.0' + path
        self._json = body
        self._status = status

    def get_response(self, request):
        return Response(self._status, create_body(self._json))
