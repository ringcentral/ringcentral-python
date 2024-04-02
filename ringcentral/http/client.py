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
        """
            Send the HTTP request and handle the response.

            Args:
                request (obj): The HTTP request object.

            Returns:
                obj: The HTTP response object.

            Raises:
                ApiException: If an error occurs during the request or response handling.
        """
        response = None

        try:
            prepared = request
            if isinstance(prepared, requests.models.Request): # not a prepared request
                prepared = request.prepare()
            response = self.load_response(prepared)

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
            Create an HTTP request object.

            Args:
                method (str): The HTTP method (e.g., GET, POST).
                url (str): The URL for the request.
                query_params (dict, optional): Dictionary containing query parameters.
                body (dict, optional): Request body data.
                headers (dict, optional): Request headers.

            Returns:
                requests.Request: The HTTP request object.

            """
        if query_params:
            if type(query_params) is dict:
                query = ""
                for key, value in  iter(query_params.items()):
                    if type(value) is list:
                        for k in value:
                            query += ("%s=%s&" % (key, k))
                    else:
                        query += ("%s=%s&" % (key, value))
                query = query[:-1]
            else:
                query = urlencode(query_params)
            if query:
                url = url + ('&' if url.find('?') > 0 else '?') + query

        content_type = None

        if headers is None:
            headers = {}

        it = iterator(headers)

        for key, value in it:
            if key.lower().find('content-type') >= 0:
                content_type = value
            if key.lower().find('accept') >= 0:
                headers['Accept'] = value

        if content_type is None:
            content_type = 'application/json'
            headers['Content-Type'] = content_type

        if content_type.lower().find('application/json') >= 0:
            body = json.dumps(body) if body else None
        elif content_type.lower().find('application/x-www-form-urlencoded') >= 0:
            body = urlencode(body) if body else None

        return requests.Request(method, url, headers=headers, data=body)
