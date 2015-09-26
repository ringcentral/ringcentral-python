#!/usr/bin/env python
# encoding: utf-8

from .mock import Mock
from time import time
from datetime import date


class Registry(object):
    def __init__(self):
        self._mocks = []

    def add(self, mock):
        self._mocks.append(mock)
        return self

    def find(self, request):

        mock = self._mocks.pop(0)

        if mock is None or not mock:
            raise Exception("No mock in registry form request %s %s" % (request.method, request.url))
        if not mock.test(request):
            raise Exception("Wrong request %s %s for expected mock %s %s" % (
                request.method, request.url, mock.method(), mock.path()))

        return mock

    def clear(self):
        self._mocks = []
        return self

    # helpers

    def generic_mock(self, method='', path='', json=None, status=None):
        return self.add(Mock(method, path, json, status))

    def authentication_mock(self):
        return self.add(Mock('POST', '/restapi/oauth/token', {
            'access_token': 'ACCESS_TOKEN',
            'token_type': 'bearer',
            'expires_in': 3600,
            'refresh_token': 'REFRESH_TOKEN',
            'refresh_token_expires_in': 60480,
            'scope': 'SMS RCM Foo Boo',
            'expireTime': time() + 3600,
            'owner_id': 'foo'
        }))

    def logout_mock(self):
        return self.add(Mock('POST', '/restapi/oauth/revoke', {}))

    def presence_subscription_mock(self, id='1', detailed=True):
        detailed = '?detailedTelephonyState=true' if detailed else ''
        expires_in = 15 * 60 * 60

        return self.add(Mock('POST', '/restapi/v1.0/subscription', {
            'eventFilters': ['/restapi/v1.0/account/~/extension/' + id + '/presence' + detailed],
            'expirationTime': date.fromtimestamp(time() + expires_in).isoformat(),
            'expiresIn': expires_in,
            'deliveryMode': {
                'transportType': 'PubNub',
                'encryption': True,
                'address': '123_foo',
                'subscriberKey': 'sub-c-foo',
                'secretKey': 'sec-c-bar',
                'encryptionAlgorithm': 'AES',
                'encryptionKey': 'e0bMTqmumPfFUbwzppkSbA=='
            },
            'creationTime': date.today().isoformat(),
            'id': 'foo-bar-baz',
            'status': 'Active',
            'uri': 'https://platform.ringcentral.com/restapi/v1.0/subscription/foo-bar-baz'
        }))

    def refresh_mock(self, failure=False, expires_in=3600):
        status = 200
        body = {
            'access_token': 'ACCESS_TOKEN_FROM_REFRESH',
            'token_type': 'bearer',
            'expires_in': expires_in,
            'refresh_token': 'REFRESH_TOKEN_FROM_REFRESH',
            'refresh_token_expires_in': 60480,
            'scope': 'SMS RCM Foo Boo',
            'expireTime': time() + expires_in,
            'owner_id': 'foo'
        }

        if failure:
            status = 400
            body = {'message': 'Wrong token (mock)'}

        return self.add(Mock('POST', '/restapi/oauth/token', body, status))

    def subscription_mock(self, expires_in=54000, filters=None):
        if filters is None:
            filters = ['/restapi/v1.0/account/~/extension/1/presence']

        return self.add(Mock('POST', '/restapi/v1.0/subscription', {
            'eventFilters': filters,
            'expirationTime': date.fromtimestamp(time() + expires_in).isoformat(),
            'expiresIn': expires_in,
            'deliveryMode': {
                'transportType': 'PubNub',
                'encryption': False,
                'address': '123_foo',
                'subscriberKey': 'sub-c-foo',
                'secretKey': 'sec-c-bar'
            },
            'id': 'foo-bar-baz',
            'creationTime': date.today().isoformat(),
            'status': 'Active',
            'uri': 'https://platform.ringcentral.com/restapi/v1.0/subscription/foo-bar-baz'
        }))