#!/usr/bin/env python
# encoding: utf-8

import unittest
from ..test import TestCase, Spy
from .response import Response


class TestSubscription(TestCase):
    def test_multipart(self):
        goodMultipartMixedResponse = "Content-Type: multipart/mixed; boundary=Boundary_1245_945802293_1394135045248\n" + \
                                     "\n" + \
                                     "--Boundary_1245_945802293_1394135045248\n" + \
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

        multipartMixedResponseWithErrorPart = "Content-Type: multipart/mixed; boundary=Boundary_1245_945802293_1394135045248\n" + \
                                              "\n" + \
                                              "--Boundary_1245_945802293_1394135045248\n" + \
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
                                              "  \"message\" : \"object not found\"\n" + \
                                              "}\n" + \
                                              "--Boundary_1245_945802293_1394135045248\n" + \
                                              "Content-Type: application/json\n" + \
                                              "\n" + \
                                              "{\n" + \
                                              "  \"baz\" : \"qux\"\n" + \
                                              "}\n" + \
                                              "--Boundary_1245_945802293_1394135045248--\n"

        badMultipartMixedResponse = "Content-Type: \n" + \
                                    "\n" + \
                                    "--Boundary_1245_945802293_1394135045248\n" + \
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

        headers = {'content-type': 'multipart/mixed; boundary=Boundary_1245_945802293_1394135045248'}

        r1 = Response(207, goodMultipartMixedResponse, headers)
        self.assertEqual(2, len(r1.get_responses()))
        self.assertEqual('bar', r1.get_responses()[0].get_json().foo)
        self.assertEqual('qux', r1.get_responses()[1].get_json().baz)

        r2 = Response(207, multipartMixedResponseWithErrorPart, headers)
        self.assertEqual('bar', r2.get_responses()[0].get_json().foo)
        self.assertEqual('object not found', r2.get_responses()[1].get_error())
        self.assertEqual('qux', r2.get_responses()[2].get_json().baz)

        r3 = Response(207, badMultipartMixedResponse, headers)
        caught = False
        try:
            r3.get_responses()
        except Exception:
            caught = True

        self.assertTrue(caught)


if __name__ == '__main__':
    unittest.main()
