#!/usr/bin/env python
# encoding: utf-8

import unittest

import core.ajax.request as request
from core.ajax.ajax import Ajax


class TestAjax(unittest.TestCase):
    def setUp(self):
        req = request.Request(request.PUT, '/restapi/v1.0/account/~/extension/~/message-store/123,123')
        self.ajax = Ajax(req)

    def test_creation(self):
        self.assertIsInstance(self.ajax, Ajax)


if __name__ == '__main__':
    unittest.main()