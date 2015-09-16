#!/usr/bin/env python
# encoding: utf-8
import json
import urllib
import requests

from ..http.api_response import ApiResponse
from ..http.client import Client as HttpClient


class Client(HttpClient):
    def __init__(self, registry):
        self._registry = registry

    def load_response(self, request):
        mock = self._registry.find(request)
        return ApiResponse(request, mock.response(request))