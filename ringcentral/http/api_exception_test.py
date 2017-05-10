#!/usr/bin/env python
# encoding: utf-8

import unittest

from ..test import TestCase
from .api_response import ApiResponse
from .api_response_test import create_response
from .api_exception import ApiException

json_headers = {'Content-Type': 'application/json'}


class TestApiException(TestCase):
    def test_simple(self):
        api_response = ApiResponse(response=create_response('{"error_description": "foo"}', 400, json_headers))
        ex = ApiException(api_response)
        self.assertEqual(str(ex), 'foo')

        api_response = ApiResponse(response=create_response('{"description": "foo"}', 400, json_headers))
        ex = ApiException(api_response)
        self.assertEqual(str(ex), 'foo')

        api_response = ApiResponse(response=create_response('{"message": "foo"}', 400, json_headers))
        ex = ApiException(api_response)
        self.assertEqual(str(ex), 'foo')


if __name__ == '__main__':
    unittest.main()
