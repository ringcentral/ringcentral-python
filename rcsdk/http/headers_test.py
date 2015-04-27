#!/usr/bin/env python
# encoding: utf-8

import unittest
from ..test import TestCase, Spy
from .headers import Headers


class TestSubscription(TestCase):
    def testIgnoresCase(self):
        h = Headers()
        self.assertEquals('foo', h.set_header('CoNtEnT-tYpE', 'foo').get_header('cOnTeNt-TyPe'))

    def testGetContentType(self):
        h = Headers()
        self.assertEquals('foo', h.set_header('CoNtEnT-tYpE', 'foo').get_content_type())

    def testSetHeadersAndGetHeadersArray(self):
        h = Headers()
        h.set_headers({'foo': 'foo', 'FOO': 'FOO', 'bar': 'bar'})
        self.assertEquals(['foo:FOO', 'bar:bar'], h.get_headers_array())

    def testIsContentType(self):
        h = Headers()
        self.assertTrue(h.set_header('Content-Type', 'fooBARfoo').is_content_type('bar'))
        self.assertTrue(h.set_header('Content-Type', 'fooBARfoo').is_content_type('FOO'))
        self.assertFalse(h.set_header('Content-Type', 'fooBARfoo').is_content_type('BAZ'))

    def testSpecialContentTypes(self):
        h = Headers()
        self.assertTrue(h.set_header('Content-Type', 'application/json; boundary=f').is_json())
        self.assertTrue(h.set_header('Content-Type', 'multipart/mixed; boundary=f').is_multipart())
        self.assertTrue(h.set_header('Content-Type', 'application/x-www-form-urlencoded; boundary=f').is_url_encoded())


if __name__ == '__main__':
    unittest.main()
