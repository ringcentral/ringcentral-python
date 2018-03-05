#!/usr/bin/env python
# encoding: utf-8

import sys
import unittest
import requests_mock

from ..test import TestCase


@requests_mock.Mocker()
class TestPlatform(TestCase):
    def test_key(self, mock):
        sdk = self.get_sdk(mock)
        self.assertEqual('d2hhdGV2ZXI6d2hhdGV2ZXI=', sdk.platform()._api_key())

    def test_login(self, mock):
        sdk = self.get_sdk(mock)
        self.assertTrue(sdk.platform().auth().data()['access_token'])

    def test_login_code(self, mock):
        sdk = self.get_sdk(mock)
        self.logout_mock(mock)
        sdk.platform().logout()
        self.authentication_mock(mock)
        sdk.platform().login(code='foo')
        text = str(mock.request_history[-1].text)
        if sys.version_info[0] == 3:
            self.assertEqual(text, 'grant_type=authorization_code&redirect_uri=mock%3A%2F%2Fwhatever-redirect&code=foo')
        else:
            self.assertEqual(text, 'code=foo&grant_type=authorization_code&redirect_uri=mock%3A%2F%2Fwhatever-redirect')

    def test_login_code_redirect(self, mock):
        sdk = self.get_sdk(mock)
        self.logout_mock(mock)
        sdk.platform().logout()
        self.authentication_mock(mock)
        sdk.platform().login(code='foo', redirect_uri='bar')
        text = str(mock.request_history[-1].text)
        if sys.version_info[0] == 3:
            self.assertEqual(text, 'grant_type=authorization_code&redirect_uri=bar&code=foo')
        else:
            self.assertEqual(text, 'code=foo&grant_type=authorization_code&redirect_uri=bar')

    def test_refresh_with_outdated_token(self, mock):
        sdk = self.get_sdk(mock)

        self.refresh_mock(mock)

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
            self.assertEqual('Refresh token has expired', str(e))

        self.assertTrue(caught)

    def test_logged_in(self, mock):
        sdk = self.get_sdk(mock)

        self.assertTrue(sdk.platform().logged_in())

    def test_manual_refresh(self, mock):
        sdk = self.get_sdk(mock)

        self.refresh_mock(mock)
        self.add(mock, 'GET', '/foo', {'foo': 'bar'})

        self.assertEqual('ACCESS_TOKEN', sdk.platform().auth().data()['access_token'])

        sdk.platform().refresh()

        self.assertEqual('ACCESS_TOKEN_FROM_REFRESH', sdk.platform().auth().data()['access_token'])

    def skip_test_automatic_refresh(self, mock):  # FIXME Put it back
        sdk = self.get_sdk(mock)

        self.add(mock, 'GET', '/foo', {'foo': 'bar'})
        self.refresh_mock(mock)

        self.assertEqual('ACCESS_TOKEN', sdk.platform().auth().data()['access_token'])

        sdk.platform().auth().set_data({
            'expires_in': 0,
            'expire_time': 0
        })

        self.assertEqual('bar', sdk.platform().get('/foo').json().foo)
        self.assertEqual('ACCESS_TOKEN_FROM_REFRESH', sdk.platform().auth().data()['access_token'])

    def test_logout(self, mock):
        sdk = self.get_sdk(mock)

        self.logout_mock(mock)

        self.assertEqual('ACCESS_TOKEN', sdk.platform().auth().data()['access_token'])

        sdk.platform().logout()

        self.assertEqual('', sdk.platform().auth().data()['access_token'])
        self.assertEqual('', sdk.platform().auth().data()['refresh_token'])
        self.assertFalse(sdk.platform().logged_in())

    def test_api_url(self, mock):
        sdk = self.get_sdk(mock)

        exp1 = 'mock://whatever/restapi/v1.0/account/~/extension/~?_method=POST&access_token=ACCESS_TOKEN'
        act1 = sdk.platform().create_url('/account/~/extension/~', add_server=True, add_method='POST', add_token=True)
        self.assertEqual(exp1, act1)

        exp2 = 'https://foo/account/~/extension/~?_method=POST&access_token=ACCESS_TOKEN'
        url2 = 'https://foo/account/~/extension/~'
        act2 = sdk.platform().create_url(url2, add_server=True, add_method='POST', add_token=True)
        self.assertEqual(exp2, act2)

    def test_api_url_custom_prefixes(self, mock):
        sdk = self.get_sdk(mock)
        exp = 'mock://whatever/scim/v2/foo'
        url = '/scim/v2/foo'
        act = sdk.platform().create_url(url, add_server=True)
        self.assertEqual(exp, act)


if __name__ == '__main__':
    unittest.main()
