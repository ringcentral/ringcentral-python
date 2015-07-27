#!/usr/bin/env python
# encoding: utf-8

import unittest
from ..test import TestCase, Spy
from .request import Request
from .request_mock import RequestMock


class TestSubscription(TestCase):
    def test_get_url_with_query_string(self):
        r = Request('GET', 'http://whatever', {'foo': 'bar', 'baz': 'qux'})
        self.assertEqual('http://whatever?foo=bar&baz=qux', r.get_url_with_query_string())

    def test_get_encoded_body(self):
        r1 = Request('POST', 'http://whatever', None, {'foo': 'bar', 'baz': 'qux'},
                     {'content-type': 'application/x-www-form-urlencoded'})
        r2 = Request('POST', 'http://whatever', None, {'foo': 'bar', 'baz': 'qux'},
                     {'content-type': 'application/json'})
        r3 = Request('POST', 'http://whatever', None, {'foo': 'bar', 'baz': 'qux'})
        r4 = Request('POST', 'http://whatever', None, 'foo-encoded-text', {'content-type': 'foo'})

        self.assertEquals('foo=bar&baz=qux', r1.get_encoded_body())
        self.assertEquals('{"foo": "bar", "baz": "qux"}', r2.get_encoded_body())
        self.assertEquals('{"foo": "bar", "baz": "qux"}', r3.get_encoded_body())  # JSON by default
        self.assertEquals('foo-encoded-text', r4.get_encoded_body())

    def test_is_methods(self):
        r1 = Request('GET', 'http://whatever')
        r2 = Request('POST', 'http://whatever')
        r3 = Request('PUT', 'http://whatever')
        r4 = Request('DELETE', 'http://whatever')

        self.assertTrue(r1.is_get() and not r1.is_post() and not r1.is_put() and not r1.is_delete())
        self.assertTrue(not r2.is_get() and r2.is_post() and not r2.is_put() and not r2.is_delete())
        self.assertTrue(not r3.is_get() and not r3.is_post() and r3.is_put() and not r3.is_delete())
        self.assertTrue(not r4.is_get() and not r4.is_post() and not r4.is_put() and r4.is_delete())

    def test_get_set_body(self):
        r = Request('GET', 'http://whatever')
        self.assertEquals('foo', r.set_body('foo').get_body())

    def test_get_set_query_params(self):
        r = Request('GET', 'http://whatever')
        self.assertEquals({'foo': 'bar'}, r.set_query_params({'foo': 'bar'}).get_query_params())

    def test_get_set_method(self):
        r = Request('GET', 'http://whatever')
        self.assertEquals('POST', r.set_method('POST').get_method())


if __name__ == '__main__':
    unittest.main()
