#!/usr/bin/env python
# encoding: utf-8

import unittest

from ..test import TestCase

class TestPlatform(TestCase):
    def test_key(self):
        sdk = self.get_sdk()
        self.assertEqual('d2hhdGV2ZXI6d2hhdGV2ZXI=', sdk.platform()._api_key())

    def test_login(self):
        sdk = self.get_sdk()
        self.assertTrue(sdk.platform().auth().data()['access_token'])

    def test_refresh_with_outdated_token(self):
        sdk = self.get_sdk()

        sdk.mock_registry().refresh_mock()

        sdk.platform().auth().set_data({
            'refresh_token_expires_in': 1,
            'refresh_token_expire_time': 1
        })

        self.assertEqual(1, sdk.platform().auth().data()['refresh_token_expires_in'])
        self.assertEqual(1, sdk.platform().auth().data()['refresh_token_expire_time'])

        caught = False
        try:
            sdk.platform().refresh()
        except Exception as e:
            caught = True
            self.assertEqual('Refresh token has expired', e.message)

        self.assertTrue(caught)

    def test_manual_refresh(self):
        sdk = self.get_sdk()

        sdk.mock_registry().refresh_mock().generic_mock('GET', '/foo', {'foo': 'bar'})

        self.assertEqual('ACCESS_TOKEN', sdk.platform().auth().data()['access_token'])

        sdk.platform().refresh()

        self.assertEqual('ACCESS_TOKEN_FROM_REFRESH', sdk.platform().auth().data()['access_token'])

    def test_automatic_refresh(self):
        sdk = self.get_sdk()

        sdk.mock_registry().refresh_mock().generic_mock('GET', '/foo', {'foo': 'bar'})

        self.assertEqual('ACCESS_TOKEN', sdk.platform().auth().data()['access_token'])

        sdk.platform().auth().set_data({
            'expires_in': 1,
            'expire_time': 1
        })

        self.assertEqual(1, sdk.platform().auth().data()['expires_in'])
        self.assertEqual(1, sdk.platform().auth().data()['expire_time'])

        self.assertEqual('bar', sdk.platform().get('/foo').json().foo)
        self.assertEqual('ACCESS_TOKEN_FROM_REFRESH', sdk.platform().auth().data()['access_token'])

    def test_logout(self):
        sdk = self.get_sdk()

        sdk.mock_registry().logout_mock()

        self.assertEqual('ACCESS_TOKEN', sdk.platform().auth().data()['access_token'])

        sdk.platform().logout()

        self.assertEqual('', sdk.platform().auth().data()['access_token'])
        self.assertEqual('', sdk.platform().auth().data()['refresh_token'])

    def test_api_url(self):
        sdk = self.get_sdk()

        exp1 = 'https://whatever/restapi/v1.0/account/~/extension/~?_method=POST&access_token=ACCESS_TOKEN'
        act1 = sdk.platform().create_url('/account/~/extension/~', add_server=True, add_method='POST', add_token=True)
        self.assertEqual(exp1, act1)

        exp2 = 'https://foo/account/~/extension/~?_method=POST&access_token=ACCESS_TOKEN'
        url2 = 'https://foo/account/~/extension/~'
        act2 = sdk.platform().create_url(url2, add_server=True, add_method='POST', add_token=True)
        self.assertEqual(exp2, act2)


if __name__ == '__main__':
    unittest.main()
