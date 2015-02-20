#!/usr/bin/env python
# encoding: utf-8

import unittest

from core.ajax.response import Response


class TestResponse(unittest.TestCase):
    def setUp(self):
        self.raw = """
HTTP/1.1 207 Multi-Status
Content-Type: multipart/mixed; boundary=Boundary_20_29214173_1373546450505

--Boundary_20_29214173_1373546450505
Content-Type: application/json

{
  "response" : [ {
    "href" : ".../account/400129284008/extension/400129284008/message-store/401654758008",
    "status" : 200,
    "responseDescription" : "OK"
  }, {
    "href" : ".../account/400129284008/extension/400129284008/message-store/401642088008",
    "status" : 200,
    "responseDescription" : "OK"
  } ]
}
--Boundary_20_29214173_1373546450505
Content-Type: application/json

{
  "uri" : ".../account/400129284008/extension/400129284008/message-store/401654758008",
  "id" : 401654758008,
  "to" : [ {
    "phoneNumber" : "18559100010"
  } ],
  "type" : "Fax",
  "creationTime" : "2013-07-11T12:05:43.000Z",
  "readStatus" : "Read",
  "priority" : "Normal",
  "attachments" : [ {
    "id" : 1,
    "uri" : ".../account/400129284008/extension/400129284008/message-store/401654758008/content/1",
    "contentType" : "image/tiff"
  } ],
  "direction" : "Outbound",
  "availability" : "Alive",
  "messageStatus" : "SendingFailed",
  "faxResolution" : "Low",
  "faxPageCount" : 0,
  "lastModifiedTime" : "2013-07-11T12:26:24.000Z"
}
--Boundary_20_29214173_1373546450505
Content-Type: application/json

{
  "uri" : ".../account/400129284008/extension/400129284008/message-store/401642088008",
  "id" : 401642088008,
  "to" : [ {
    "phoneNumber" : "77653287256446"
  } ],
  "type" : "Fax",
  "creationTime" : "2013-07-11T08:45:57.000Z",
  "readStatus" : "Read",
  "priority" : "Normal",
  "attachments" : [ {
    "id" : 1,
    "uri" : ".../account/400129284008/extension/400129284008/message-store/401642088008/content/1",
    "contentType" : "image/tiff"
  } ],
  "direction" : "Outbound",
  "availability" : "Alive",
  "messageStatus" : "SendingFailed",
  "faxResolution" : "Low",
  "faxPageCount" : 0,
  "lastModifiedTime" : "2013-07-11T12:26:52.000Z"
}
--Boundary_20_29214173_1373546450505--
    """

    def test_creation(self):
        r = Response(200, self.raw)
        self.assertIsInstance(r, Response)
        self.assertTrue(r.is_multipart())

