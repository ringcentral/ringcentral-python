#!/usr/bin/env python
# encoding: utf-8

import unittest
from ..test import TestCase, Spy
from ..http.mocks.presence_subscription_mock import PresenceSubscriptionMock
from ..http.mocks.subscription_mock import SubscriptionMock
from . import *


class TestSubscription(TestCase):
    def test_presence_decryption(self):
        sdk = self.get_sdk()

        sdk.get_context().get_mocks().add(PresenceSubscriptionMock())

        aes_message = 'gkw8EU4G1SDVa2/hrlv6+0ViIxB7N1i1z5MU/Hu2xkIKzH6yQzhr3vIc27IAN558kTOkacqE5DkLpRdnN1orwtIBsUHm' + \
                      'PMkMWTOLDzVr6eRk+2Gcj2Wft7ZKrCD+FCXlKYIoa98tUD2xvoYnRwxiE2QaNywl8UtjaqpTk1+WDImBrt6uabB1WICY' + \
                      '/qE0It3DqQ6vdUWISoTfjb+vT5h9kfZxWYUP4ykN2UtUW1biqCjj1Rb6GWGnTx6jPqF77ud0XgV1rk/Q6heSFZWV/GP2' + \
                      '3/iytDPK1HGJoJqXPx7ErQU='

        s = sdk.get_subscription()
        spy = Spy()

        s.add_events(['/restapi/v1.0/account/~/extension/1/presence'])
        s.on(EVENTS['notification'], spy)
        s.register()
        s._get_pubnub().receive_message(aes_message)

        expected = {
            "timestamp": "2014-03-12T20:47:54.712+0000",
            "body": {
                "extensionId": 402853446008,
                "telephonyStatus": "OnHold"
            },
            "event": "/restapi/v1.0/account/~/extension/402853446008/presence",
            "uuid": "db01e7de-5f3c-4ee5-ab72-f8bd3b77e308"
        }

        self.assertEqual(expected, spy.args[0])

        s.destroy()

    def test_plain_subscription(self):
        sdk = self.get_sdk()

        sdk.get_context().get_mocks().add(SubscriptionMock())

        s = sdk.get_subscription()
        spy = Spy()
        expected = {
            "timestamp": "2014-03-12T20:47:54.712+0000",
            "body": {
                "extensionId": 402853446008,
                "telephonyStatus": "OnHold"
            },
            "event": "/restapi/v1.0/account/~/extension/402853446008/presence",
            "uuid": "db01e7de-5f3c-4ee5-ab72-f8bd3b77e308"
        }

        s.add_events(['/restapi/v1.0/account/~/extension/1/presence'])
        s.on(EVENTS['notification'], spy)
        s.register()
        s._get_pubnub().receive_message(expected)

        self.assertEqual(expected, spy.args[0])

        s.destroy()

    def test_subscribe_with_events(self):
        sdk = self.get_sdk()

        sdk.get_context().get_mocks().add(SubscriptionMock())

        s = sdk.get_subscription()
        res = s.register(events=['/restapi/v1.0/account/~/extension/1/presence'])

        self.assertEqual('/restapi/v1.0/account/~/extension/1/presence', res.get_json().eventFilters[0])

        s.destroy()


if __name__ == '__main__':
    unittest.main()
