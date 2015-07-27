#!/usr/bin/env python
# encoding: utf-8

from ..response import Response
import json


class Mock(object):
    def __init__(self):
        self._path = ''

    def get_response(self, request):
        return Response(200, '{}')

    def test(self, request):
        # print('Testing path', request.get_url(), 'against mock path', self._path)
        return request.get_url().find(self._path) >= 0


def create_body(body):
    return json.dumps(body)

