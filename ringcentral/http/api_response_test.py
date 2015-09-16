#!/usr/bin/env python
# encoding: utf-8

import unittest

from ..test import TestCase
from api_response import ApiResponse
from requests import Response

multipart_headers = {'Content-Type': 'multipart/mixed; boundary=Boundary_1245_945802293_1394135045248'}


class TestApiResponse(TestCase):
    def test_multipart(self):
        response = "--Boundary_1245_945802293_1394135045248\n" + \
                   "Content-Type: application/json\r\n" + \
                   "\r\n" + \
                   "{\n" + \
                   "  \"response\" : [ {\n" + \
                   "    \"status\" : 200\n" + \
                   "  }, {\n" + \
                   "    \"status\" : 200\n" + \
                   "  } ]\n" + \
                   "}\n" + \
                   "--Boundary_1245_945802293_1394135045248\n" + \
                   "Content-Type: application/json\n" + \
                   "\n" + \
                   "{\n" + \
                   "  \"foo\" : \"bar\"\n" + \
                   "}\n" + \
                   "--Boundary_1245_945802293_1394135045248\n" + \
                   "Content-Type: application/json\n" + \
                   "\n" + \
                   "{\n" + \
                   "  \"baz\" : \"qux\"\n" + \
                   "}\n" + \
                   "--Boundary_1245_945802293_1394135045248--\n"

        r = ApiResponse(response=create_response(response, 207, multipart_headers))

        self.assertEqual(2, len(r.multipart()))
        self.assertEqual('bar', r.multipart()[0].json().foo)
        self.assertEqual('qux', r.multipart()[1].json().baz)

    def test_multipart_with_error(self):
        response = "--Boundary_1245_945802293_1394135045248\n" + \
                   "Content-Type: application/json\n" + \
                   "\n" + \
                   "{\n" + \
                   "  \"response\" : [ {\n" + \
                   "    \"status\" : 200\n" + \
                   "  }, {\n" + \
                   "    \"status\" : 404\n" + \
                   "  }, {\n" + \
                   "    \"status\" : 200\n" + \
                   "  } ]\n" + \
                   "}\n" + \
                   "--Boundary_1245_945802293_1394135045248\n" + \
                   "Content-Type: application/json\n" + \
                   "\n" + \
                   "{\n" + \
                   "  \"foo\" : \"bar\"\n" + \
                   "}\n" + \
                   "--Boundary_1245_945802293_1394135045248\n" + \
                   "Content-Type: application/json\n" + \
                   "\n" + \
                   "{\n" + \
                   "  \"error_description\" : \"object not found\"\n" + \
                   "}\n" + \
                   "--Boundary_1245_945802293_1394135045248\n" + \
                   "Content-Type: application/json\n" + \
                   "\n" + \
                   "{\n" + \
                   "  \"baz\" : \"qux\"\n" + \
                   "}\n" + \
                   "--Boundary_1245_945802293_1394135045248--\n"

        r = ApiResponse(response=create_response(response, 207, multipart_headers))

        self.assertEqual('bar', r.multipart()[0].json().foo)
        self.assertEqual('object not found', r.multipart()[1].error())
        self.assertEqual('qux', r.multipart()[2].json().baz)

    def test_multipart_bad_response(self):
        response = "--Boundary_1245_945802293_1394135045248\n" + \
                   "Content-Type: application/json\n" + \
                   "\n" + \
                   "THIS IS JUNK AND CANNOT BE PARSED AS JSON\n" + \
                   "--Boundary_1245_945802293_1394135045248\n" + \
                   "Content-Type: application/json\n" + \
                   "\n" + \
                   "{\n" + \
                   "  \"foo\" : \"bar\"\n" + \
                   "}\n" + \
                   "--Boundary_1245_945802293_1394135045248\n" + \
                   "Content-Type: application/json\n" + \
                   "\n" + \
                   "{\n" + \
                   "  \"baz\" : \"qux\"\n" + \
                   "}\n" + \
                   "--Boundary_1245_945802293_1394135045248--\n"

        r = ApiResponse(response=create_response(response, 207, multipart_headers))

        with self.assertRaises(Exception) as e:
            r.multipart()


def create_response(body, status, headers=None):
    res = Response()
    res.headers = headers
    res._content = body
    res.status_code = status
    return res


if __name__ == '__main__':
    unittest.main()
