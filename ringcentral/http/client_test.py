#!/usr/bin/env python
# encoding: utf-8

import unittest

from ..test import TestCase
from .client import Client

body = {'foo': 'bar', 'baz': 'qux'}


class TestClient(TestCase):
    def test_create_request_with_query_string(self):
        req = Client().create_request(url='http://whatever', query_params={'foo': 'bar', 'baz': 'qux'})
        self.assertEqual('http://whatever?foo=bar&baz=qux', req.url)

        req = Client().create_request(url='http://whatever', query_params={'a2z':['abc','xyz']})
        self.assertEqual('http://whatever?a2z=abc&a2z=xyz', req.url)

    def test_create_request_encode_body_url(self):
        r = Client().create_request(body=body, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.assertEqual('foo=bar&baz=qux', r.data)

    def test_create_request_encode_body_json(self):
        r = Client().create_request(body=body, headers={'Content-Type': 'application/json'})
        self.assertEqual('{"foo": "bar", "baz": "qux"}', r.data)

    def test_create_request_encode_body_json_default(self):
        r = Client().create_request(body=body)  # JSON by default
        self.assertEqual('{"foo": "bar", "baz": "qux"}', r.data)

    def test_create_request_encode_body_alternative(self):
        r = Client().create_request(body='foo-encoded-text', headers={'content-type': 'foo'})
        self.assertEqual('foo-encoded-text', r.data)


if __name__ == '__main__':
    unittest.main()
