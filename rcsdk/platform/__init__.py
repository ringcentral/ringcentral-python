#!/usr/bin/env python
# encoding: utf-8

import base64
from .auth import Auth
from ..http.request import *
from ..http.response import *


ACCOUNT_ID = '~'
ACCOUNT_PREFIX = '/account/'
URL_PREFIX = '/restapi'
TOKEN_ENDPOINT = '/restapi/oauth/token'
REVOKE_ENDPOINT = '/restapi/oauth/revoke'
API_VERSION = 'v1.0'
ACCESS_TOKEN_TTL = 3600  # 60 minutes
REFRESH_TOKEN_TTL = 36000  # 10 hours
REFRESH_TOKEN_TTL_REMEMBER = 604800  # 1 week


class Platform:
    def __init__(self, context, key, secret, server):
        self.__context = context
        self.__server = server
        self.appKey = key
        self.appSecret = secret
        self.__auth = Auth()
        self.__account = ACCOUNT_ID

    def set_auth_data(self, auth_data=None):
        self.__auth.set_data(auth_data)
        return self

    def get_auth_data(self):
        return self.__auth.get_data()

    def is_authorized(self, refresh=True):
        if not self.__auth.is_access_token_valid() and refresh:
            self.refresh()
        if not self.__auth.is_access_token_valid():
            raise Exception('Access token is not valid after refresh timeout')

    def authorize(self, user_name, extension, password, remember=False):
        response = self.__auth_call(POST, TOKEN_ENDPOINT, body={
            'grant_type': 'password',
            'username': user_name,
            'extension': extension,
            'password': password,
            'access_token_ttl': ACCESS_TOKEN_TTL,
            'refresh_token_ttl': REFRESH_TOKEN_TTL_REMEMBER if remember else REFRESH_TOKEN_TTL
        })
        self.__auth.set_data(response.get_json(False))
        self.__auth.set_remember(remember)

    def refresh(self):
        if not self.__auth.is_refresh_token_valid():
            raise Exception('Refresh token has expired')

        response = self.__auth_call(POST, TOKEN_ENDPOINT, body={
            'grant_type': 'refresh_token',
            'refresh_token': self.__auth.get_refresh_token(),
            'access_token_ttl': ACCESS_TOKEN_TTL,
            'refresh_token_ttl': REFRESH_TOKEN_TTL_REMEMBER if self.__auth.is_remember() else REFRESH_TOKEN_TTL
        })

        self.__auth.set_data(response.get_json(False))

        return response

    def logout(self):
        response = self.__auth_call(POST, REVOKE_ENDPOINT, body={
            'token': self.__auth.get_access_token
        })
        self.__auth.reset()
        return response

    def __api_call(self, method, url, query_params=None, body=None, headers=None):
        self.is_authorized()
        request = self.__context.get_request(method, url, query_params, body, headers)
        request.set_header(AUTHORIZATION, self.__auth.get_token_type() + ' ' + self.__get_access_token())
        request.set_url(self.api_url(request.get_url(), add_server=True))
        return request.send()

    def __auth_call(self, method, url, query_params=None, body=None, headers=None):
        request = self.__context.get_request(method, url, query_params, body, headers)
        request.set_header(AUTHORIZATION, 'Basic ' + self.get_api_key())
        request.set_header(CONTENT_TYPE, URL_ENCODED_CONTENT_TYPE)
        request.set_url(self.api_url(request.get_url(), add_server=True))
        request.set_method(POST)
        return request.send()

    def get_api_key(self):
        return base64.b64encode(self.appKey + ':' + self.appSecret)

    def __get_access_token(self):
        return self.__auth.get_access_token()

    def api_url(self, url, add_server=False, add_method=None, add_token=False):
        built_url = ''
        has_http = url.find('http://') >= 0 or url.find('https://') >= 0

        if add_server and not has_http:
            built_url += self.__server

        if url.find(URL_PREFIX) < 0 and not has_http:
            built_url += URL_PREFIX + '/' + API_VERSION

        if url.find(ACCOUNT_PREFIX) >= 0:
            built_url = built_url.replace(ACCOUNT_PREFIX + ACCOUNT_ID, ACCOUNT_PREFIX + self.__account)

        built_url += url

        if add_method:
            built_url += ('&' if built_url.find('?') >= 0 else '?') + '_method=' + add_method

        if add_token:
            built_url += ('&' if built_url.find('?') >= 0 else '?') + 'access_token=' + self.__get_access_token()

        return built_url

    def get(self, url, query_params=None, headers=None):
        return self.__api_call(GET, url, query_params, None, headers)

    def post(self, url, query_params=None, body=None, headers=None):
        return self.__api_call(POST, url, query_params, body, headers)

    def put(self, url, query_params=None, body=None, headers=None):
        return self.__api_call(PUT, url, query_params, body, headers)

    def delete(self, url, query_params=None, body=None, headers=None):
        return self.__api_call(DELETE, url, query_params, body, headers)