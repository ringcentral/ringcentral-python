#!/usr/bin/env python
# encoding: utf-8

from .mock import *
from ..response import Response
from time import gmtime


class LogoutMock(Mock):
    def __init__(self):
        Mock.__init__(self)

        self._path = '/restapi/oauth/revoke'

    def get_response(self, request):
        return Response(200, create_body({}))