#!/usr/bin/env python
# encoding: utf-8

import unittest
import requests_mock

from ..test import TestCase, Spy
from .subscription import *


@requests_mock.Mocker()
class TestSubscription(TestCase):
    def test_presence_decryption(self, mock):
        sdk = self.get_sdk(mock)

        self.presence_subscription_mock(mock)

        aes_message = 'gkw8EU4G1SDVa2/hrlv6+0ViIxB7N1i1z5MU/Hu2xkIKzH6yQzhr3vIc27IAN558kTOkacqE5DkLpRdnN1orwtIBsUHm' + \
                      'PMkMWTOLDzVr6eRk+2Gcj2Wft7ZKrCD+FCXlKYIoa98tUD2xvoYnRwxiE2QaNywl8UtjaqpTk1+WDImBrt6uabB1WICY' + \
                      '/qE0It3DqQ6vdUWISoTfjb+vT5h9kfZxWYUP4ykN2UtUW1biqCjj1Rb6GWGnTx6jPqF77ud0XgV1rk/Q6heSFZWV/GP2' + \
                      '3/iytDPK1HGJoJqXPx7ErQU='

        expected = {
            "timestamp": "2014-03-12T20:47:54.712+0000",
            "body": {
                "extensionId": 402853446008,
                "telephonyStatus": "OnHold"
            },
            "event": "/restapi/v1.0/account/~/extension/402853446008/presence",
            "uuid": "db01e7de-5f3c-4ee5-ab72-f8bd3b77e308"
        }

        s = sdk.create_subscription()

        try:
            spy = Spy()

            s.add_events(['/restapi/v1.0/account/~/extension/1/presence'])
            s.on(Events.notification, spy)
            s.register()

            self.assertEqual(expected, s._decrypt(aes_message))

        finally:
            s.destroy()

    def test_plain_subscription(self, mock):
        sdk = self.get_sdk(mock)

        self.subscription_mock(mock)

        s = sdk.create_subscription()

        expected = {
            "timestamp": "2014-03-12T20:47:54.712+0000",
            "body": {
                "extensionId": 402853446008,
                "telephonyStatus": "OnHold"
            },
            "event": "/restapi/v1.0/account/~/extension/402853446008/presence",
            "uuid": "db01e7de-5f3c-4ee5-ab72-f8bd3b77e308"
        }

        try:
            spy = Spy()

            s.add_events(['/restapi/v1.0/account/~/extension/1/presence'])
            s.on(Events.notification, spy)
            s.register()
            s._notify(expected)

            self.assertEqual(expected, spy.args[0])
            self.assertNotEqual(s.pubnub(), None)

        finally:
            s.destroy()

    def test_subscribe_error(self, mock):
        sdk = self.get_sdk(mock)

        s = sdk.create_subscription()

        self.add(mock, 'POST', '/restapi/v1.0/subscription', {'error_description': 'expected'}, 400)

        try:
            s.add_events(['/restapi/v1.0/account/~/extension/1/presence'])
            s.register()
            raise Exception('This should not be reached')

        except Exception as e:
            self.assertEqual(str(e), 'expected')
        finally:
            s.destroy()

    def test_subscribe_with_events_and_renew(self, mock):
        sdk = self.get_sdk(mock)

        s = sdk.create_subscription()

        try:
            self.subscription_mock(mock)
            res = s.register(events=['/restapi/v1.0/account/~/extension/1/presence'])
            self.assertEqual('/restapi/v1.0/account/~/extension/1/presence', res.json().eventFilters[0])

            self.subscription_mock(mock, id='foo-bar-baz', filters=['/restapi/v1.0/account/~/extension/1/foo'])
            res = s.renew()
            self.assertEqual('/restapi/v1.0/account/~/extension/1/foo', res.json().eventFilters[0])

        finally:
            s.destroy()

    def test_subscribe_with_no_events(self, mock):
        sdk = self.get_sdk(mock)

        s = sdk.create_subscription()

        try:
            self.subscription_mock(mock)
            s.register()
            raise Exception('This should not be reached')

        except Exception as e:
            self.assertEqual(str(e), 'Events are undefined')

        finally:
            s.destroy()

    def test_subscribe_remove(self, mock):
        sdk = self.get_sdk(mock)

        s = sdk.create_subscription()

        try:
            self.subscription_mock(mock)
            s.register(events=['/restapi/v1.0/account/~/extension/1/presence'])

            self.add(mock, 'DELETE', '/restapi/v1.0/subscription/foo-bar-baz', {}, 204)
            s.remove()

        finally:
            s.destroy()

    def test_subscribe_remove_error(self, mock):
        sdk = self.get_sdk(mock)

        s = sdk.create_subscription()

        try:
            self.subscription_mock(mock)
            s.register(events=['/restapi/v1.0/account/~/extension/1/presence'])

            self.add(mock, 'DELETE', '/restapi/v1.0/subscription/foo-bar-baz', {'error_description': 'expected'}, 400)
            s.remove()

            raise Exception('This should not be reached')

        except Exception as e:
            self.assertEqual(str(e), 'expected')

        finally:
            s.destroy()


if __name__ == '__main__':
    unittest.main()
