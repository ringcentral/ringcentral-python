#!/usr/bin/env python
# encoding: utf-8

import unittest
from .. import SDK


class TestCase(unittest.TestCase):
    def __init__(self, method_name=None):
        unittest.TestCase.__init__(self, method_name)

    def get_sdk(self, authorized=True):
        sdk = SDK('whatever', 'whatever', 'https://whatever', use_http_mock=True, use_pubnub_mock=True)

        if authorized:
            sdk.mock_registry().authentication_mock()
            sdk.platform().login('18881112233', None, 'password')

        return sdk
