#!/usr/bin/env python
# encoding: utf-8
import json
import urllib
import requests

from .api_response import ApiResponse
from .api_exception import ApiException
from ..core import urlencode, iterator


class Client:
    def __init__(self):
        pass

    def send(self, request):
        response = None

        try:
            response = self.load_response(request.prepare())

            if response.ok():
                return response
            else:
                response.response().raise_for_status()

        except Exception as e:
            if response is None:
                response = ApiResponse(request)

            raise ApiException(response, e)

    def load_response(self, request):
        # TODO Persist between requests?
        session = None

        try:
            session = requests.sessions.Session()
            response = session.send(request)
            session.close()

            return ApiResponse(request, response)

        except Exception:
            if session:
                session.close()
            raise

    def create_request(self, method='', url='', query_params=None, body=None, headers=None):
        """
        :param method:
        :param url:
        :param query_params:
        :param body:
        :param headers:
        :return:requests.Request
        """

        if query_params:
            query = urlencode(query_params)
            if query:
                url = url + ('&' if url.find('?') > 0 else '?') + query

        content_type = None
        accept = None

        if headers is None:
            headers = {}

        it = iterator(headers)

        for key, value in it:
            if key.lower().find('content-type') >= 0:
                content_type = value
            if key.lower().find('accept') >= 0:
                accept = value

        if content_type is None:
            content_type = 'application/json'
            headers['Content-Type'] = content_type

        if accept is None:
            accept = 'application/json'
            headers['Accept'] = accept

        if content_type.lower().find('application/json') >= 0:
            body = json.dumps(body) if body else None
        elif content_type.lower().find('application/x-www-form-urlencoded') >= 0:
            body = urlencode(body) if body else None

        return requests.Request(method, url, headers=headers, data=body)
