#!/usr/bin/env python
# encoding: utf-8

from .mock import *
from ..response import Response
from time import time


class RefreshMock(Mock):
    def __init__(self, failure=False, expires_in=3600):
        Mock.__init__(self)

        self._path = '/restapi/oauth/token'
        self._failure = failure
        self._expires_in = expires_in

    def get_response(self, request):
        if not self._failure:
            return Response(200, create_body({
                'access_token': 'ACCESS_TOKEN_FROM_REFRESH',
                'token_type': 'bearer',
                'expires_in': self._expires_in,
                'refresh_token': 'REFRESH_TOKEN_FROM_REFRESH',
                'refresh_token_expires_in': 60480,
                'scope': 'SMS RCM Foo Boo',
                'expireTime': time() + self._expires_in,
                'owner_id': 'foo'
            }))

        else:
            return Response(400, create_body({'message': 'Wrong token (mock)'}))

    def test(self, request):
        body = request.get_body()
        return Mock.test(self, request) and body and 'grant_type' in body and body['grant_type'] == 'refresh_token'