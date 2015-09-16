#!/usr/bin/env python
# encoding: utf-8

import json as _json
import requests


class Mock(object):
    def __init__(self, method='GET', path='', json=None, status=200):
        self._method = method
        self._path = path
        self._json = json
        self._status = status

    def response(self, request):
        res = requests.Response()
        res.headers = {'Content-Type': 'application/json'}
        res._content = _json.dumps(self._json)
        res.status_code = self._status
        return res

    def test(self, request):
        return request.url.find(self._path) >= 0 and request.method.upper() == self._method.upper()

    def method(self):
        return self._method

    def path(self):
        return self._path