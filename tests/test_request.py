#!/usr/bin/env python
# encoding: utf-8

import unittest

from core.ajax.request import *


class TestRequest(unittest.TestCase):
    def setUp(self):
        pass

    def test_creation(self):
        r = Request(PUT, '/restapi/v1.0/account/~/extension/~/message-store/123,123')
        self.assertIsInstance(r, Request)


if __name__ == '__main__':
    unittest.main()