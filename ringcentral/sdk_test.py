#!/usr/bin/env python
# encoding: utf-8

import unittest
from .test import TestCase
from . import SDK


class TestSDK(TestCase):
    def test_instance(self):
        sdk = SDK('whatever', 'whatever', 'https://whatever', use_pubnub_mock=True)
        self.assertEqual(sdk.platform().create_url('/foo', add_server=True), 'https://whatever/restapi/v1.0/foo')


if __name__ == '__main__':
    unittest.main()
