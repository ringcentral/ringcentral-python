import unittest
import requests_mock
import json
import re
from time import time
from datetime import date
from .. import SDK

requests_mock.Mocker.TEST_PREFIX = 'test'


class TestCase(unittest.TestCase):
    def __init__(self, method_name=None):
        unittest.TestCase.__init__(self, method_name)

    def get_sdk(self, mock):
        sdk = SDK('whatever', 'whatever', 'https://whatever', redirect_uri='https://whatever-redirect')
        self.authentication_mock(mock)
        sdk.platform().login(jwt='jwt-token')
        return sdk

    def add(self, mock, method, url, body, status=200):
        mock.register_uri(
            method=method,
            url='https://whatever' + url,
            text= '' if body is None else json.dumps(body),
            headers={'Content-Type': 'application/json'},
            status_code=status
        )

    def authentication_mock(self, mock):
        return self.add(mock, 'POST', '/restapi/oauth/token', {
            'access_token': 'ACCESS_TOKEN',
            'token_type': 'bearer',
            'expires_in': 3600,
            'refresh_token': 'REFRESH_TOKEN',
            'refresh_token_expires_in': 60480,
            'scope': 'SMS RCM Foo Boo',
            'expireTime': time() + 3600,
            'owner_id': 'foo'
        })

    def logout_mock(self, mock):
        return self.add(mock, 'POST', '/restapi/oauth/revoke', {})

    def presence_subscription_mock(self, mock, id='1', detailed=True):
        detailed = '?detailedTelephonyState=true' if detailed else ''
        expires_in = 15 * 60 * 60

        return self.add(mock, 'POST', '/restapi/v1.0/subscription', {
            'eventFilters': ['/restapi/v1.0/account/~/extension/' + id + '/presence' + detailed],
            'expirationTime': date.fromtimestamp(time() + expires_in).isoformat(),
            'expiresIn': expires_in,
            'deliveryMode': {
                'transportType': 'WebSocket',
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
        })

    def refresh_mock(self, mock, failure=False, expires_in=3600):
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

        return self.add(mock, 'POST', '/restapi/oauth/token', body, status)

    def subscription_mock(self, mock, expires_in=54000, filters=None, id=None):
        if filters is None:
            filters = ['/restapi/v1.0/account/~/extension/1/presence']

        return self.add(mock, 'POST' if not id else 'PUT', '/restapi/v1.0/subscription' + ('/' + id if id else ''), {
            'eventFilters': filters,
            'expirationTime': date.fromtimestamp(time() + expires_in).isoformat(),
            'expiresIn': expires_in,
            'deliveryMode': {
                'transportType': 'WebSocket',
                'encryption': False,
                'address': '123_foo',
                'subscriberKey': 'sub-c-foo',
                'secretKey': 'sec-c-bar'
            },
            'id': id if id else 'foo-bar-baz',
            'creationTime': date.today().isoformat(),
            'status': 'Active',
            'uri': 'https://platform.ringcentral.com/restapi/v1.0/subscription/foo-bar-baz'
        })

    def delete_mock_with_body(self,mock):
        return self.add(mock, 'DELETE', '/restapi/v2/accounts/~/extensions', {"keepAssetsInInventory": True,"records": [{"id": "123"}]})

    def delete_mock_without_body(self,mock):
        return self.add(mock, 'DELETE', '/restapi/v2/accounts/~/extensions', body=None)