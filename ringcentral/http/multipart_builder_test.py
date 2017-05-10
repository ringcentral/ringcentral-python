#!/usr/bin/env python
# encoding: utf-8

import unittest

from ..test import TestCase
from .multipart_builder import MultipartBuilder


class TestMultipartBuilder(TestCase):
    def test_add(self):
        mb = MultipartBuilder()

        mb.set_body({'foo': 'bar'})
        mb.add(('report.csv', 'some,data,to,send'))

        req = mb.request('/foo')

        self.assertEqual(mb.body(), {'foo': 'bar'})
        self.assertEqual(mb.contents(), [('attachment', ('report.csv', 'some,data,to,send'))])
        self.assertEqual(req.files, [
            ('json', ('request.json', '{"foo": "bar"}', 'application/json')),
            ('attachment', ('report.csv', 'some,data,to,send'))
        ])


if __name__ == '__main__':
    unittest.main()
