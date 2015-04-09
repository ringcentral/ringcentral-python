#!/usr/bin/env python
# encoding: utf-8

from .mock import *
from ..response import Response
from time import time


class AuthenticationMock(Mock):
    def __init__(self):
        Mock.__init__(self)

        self._path = '/restapi/oauth/token'

    def get_response(self, request):
        return Response(200, create_body({
            'access_token': 'ACCESS_TOKEN',
            'token_type': 'bearer',
            'expires_in': 3600,
            'refresh_token': 'REFRESH_TOKEN',
            'refresh_token_expires_in': 60480,
            'scope': 'SMS RCM Foo Boo',
            'expireTime': time() + 3600,
            'owner_id': 'foo'
        }))

    def test(self, request):
        body = request.get_body()
        return Mock.test(self, request) and body and 'grant_type' in body and body['grant_type'] == 'password'