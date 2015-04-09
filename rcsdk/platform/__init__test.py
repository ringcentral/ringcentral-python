#!/usr/bin/env python
# encoding: utf-8

import unittest
from ..test import TestCase
from ..http.mocks.refresh_mock import RefreshMock
from ..http.mocks.generic_mock import GenericMock
from ..http.mocks.logout_mock import LogoutMock


class TestPlatform(TestCase):
    def test_key(self):
        sdk = self.get_sdk(False)
        self.assertEqual('d2hhdGV2ZXI6d2hhdGV2ZXI=', sdk.get_platform().get_api_key())

    def test_login(self):
        sdk = self.get_sdk()
        self.assertTrue(sdk.get_platform().get_auth_data()['access_token'])

    def test_refresh_with_outdated_token(self):
        sdk = self.get_sdk()

        sdk.get_context().get_mocks().add(RefreshMock())

        sdk.get_platform().set_auth_data({
            'refresh_token_expires_in': 1,
            'refresh_token_expire_time': 1
        })

        self.assertEqual(1, sdk.get_platform().get_auth_data()['refresh_token_expires_in'])
        self.assertEqual(1, sdk.get_platform().get_auth_data()['refresh_token_expire_time'])

        caught = False
        try:
            sdk.get_platform().refresh()
        except Exception as e:
            caught = True
            self.assertEqual('Refresh token has expired', e.message)

        self.assertTrue(caught)

    def test_manual_refresh(self):
        sdk = self.get_sdk()

        sdk.get_context().get_mocks().add(RefreshMock()).add(GenericMock('/foo', {'foo': 'bar'}))

        self.assertEqual('ACCESS_TOKEN', sdk.get_platform().get_auth_data()['access_token'])

        sdk.get_platform().refresh()

        self.assertEqual('ACCESS_TOKEN_FROM_REFRESH', sdk.get_platform().get_auth_data()['access_token'])

    def test_automatic_refresh(self):
        sdk = self.get_sdk()

        sdk.get_context().get_mocks().add(RefreshMock()).add(GenericMock('/foo', {'foo': 'bar'}))

        self.assertEqual('ACCESS_TOKEN', sdk.get_platform().get_auth_data()['access_token'])

        sdk.get_platform().set_auth_data({
            'expires_in': 1,
            'expire_time': 1
        })

        self.assertEqual(1, sdk.get_platform().get_auth_data()['expires_in'])
        self.assertEqual(1, sdk.get_platform().get_auth_data()['expire_time'])

        self.assertEqual('bar', sdk.get_platform().get('/foo').get_json().foo)
        self.assertEqual('ACCESS_TOKEN_FROM_REFRESH', sdk.get_platform().get_auth_data()['access_token'])

    def test_logout(self):
        sdk = self.get_sdk()

        sdk.get_context().get_mocks().add(LogoutMock())

        self.assertEqual('ACCESS_TOKEN', sdk.get_platform().get_auth_data()['access_token'])

        sdk.get_platform().logout()

        self.assertEqual('', sdk.get_platform().get_auth_data()['access_token'])
        self.assertEqual('', sdk.get_platform().get_auth_data()['refresh_token'])

    def test_api_url(self):
        sdk = self.get_sdk()

        exp1 = 'https://whatever/restapi/v1.0/account/~/extension/~?_method=POST&access_token=ACCESS_TOKEN'
        act1 = sdk.get_platform().api_url('/account/~/extension/~', add_server=True, add_method='POST', add_token=True)
        self.assertEqual(exp1, act1)

        exp2 = 'https://foo/account/~/extension/~?_method=POST&access_token=ACCESS_TOKEN'
        url2 = 'https://foo/account/~/extension/~'
        act2 = sdk.get_platform().api_url(url2, add_server=True, add_method='POST', add_token=True)
        self.assertEqual(exp2, act2)


if __name__ == '__main__':
    unittest.main()
