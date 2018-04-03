#!/usr/bin/env python
# encoding: utf-8

import unittest

from ..test import TestCase
from .multipart_builder import MultipartBuilder

class MockPlatform:
    def create_url(self, url, add_server):
        if add_server:
            return 'http://example.com/' + url
        return url

class TestMultipartBuilder(TestCase):
    def test_add(self):
        mb = MultipartBuilder(MockPlatform())

        mb.set_body({'foo': 'bar'})
        mb.add(('report.csv', 'some,data,to,send'))

        req = mb.request('/foo')

        self.assertEqual(mb.body(), {'foo': 'bar'})
        self.assertEqual(mb.contents(), [('attachment', ('report.csv', 'some,data,to,send'))])
        self.assertEqual(req.files, [
            ('json', ('request.json', '{"foo": "bar"}', 'application/json')),
            ('attachment', ('report.csv', 'some,data,to,send'))
        ])

    def test_multipart_mixed(self):
        mb = MultipartBuilder(MockPlatform())

        mb.set_body({'foo': 'bar'})
        mb.add(('report.csv', 'some,data,to,send'))
        mb.set_multipart_mixed(True)

        req = mb.request('/foo')

        self.assertTrue('multipart/mixed' in req.headers['Content-Type'], True)
        self.assertEqual(mb.body(), {'foo': 'bar'})
        self.assertEqual(mb.contents(), [('attachment', ('report.csv', 'some,data,to,send'))])


if __name__ == '__main__':
    unittest.main()
