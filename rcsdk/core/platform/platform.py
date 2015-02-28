#!/usr/bin/env python
# encoding: utf-8

import base64
import time

from .auth import Auth
from core.ajax.request import *
from core.ajax.ajax import Ajax

ACCOUNT_ID = '~'
ACCOUNT_PREFIX = '/account/'
URL_PREFIX = '/restapi'
TOKEN_ENDPOINT = '/restapi/oauth/token'
API_VERSION = 'v1.0'
ACCESS_TOKEN_TTL = 600  # 10 minutes
REFRESH_TOKEN_TTL = 36000  # 10 hours
REFRESH_TOKEN_TTL_REMEMBER = 604800  # 1 week
SERVER = 'https://platform.ringcentral.com'


class Platform:
    def __init__(self, cache, key, secret, server=None):
        self.__server = server if server else SERVER
        self.appKey = key
        self.appSecret = secret
        self.__auth = Auth(cache)
        self.__account = ACCOUNT_ID

    def is_authorized(self, refresh=True):
        if not self.__auth.is_access_token_valid() and refresh:
            self.refresh()
        if not self.__auth.is_access_token_valid():
            raise Exception('Access token is not valid after refresh timeout')

    def authorize(self, user_name, extension, password, remember=False):
        ajax = self.auth_call(Request(POST, TOKEN_ENDPOINT, body={
            'grant_type': 'password',
            'username': user_name,
            'extension': extension,
            'password': password,
            'access_toket_ttl': ACCESS_TOKEN_TTL,
            'refresh_token_ttl': REFRESH_TOKEN_TTL_REMEMBER if remember else REFRESH_TOKEN_TTL
        }))
        self.__auth.set_data(ajax.get_response().get_data())
        self.__auth.set_remember(remember)

    def refresh(self):
        if not self.__auth.is_paused():

            print("Refresh will be performed\n")
            self.__auth.pause()

            if not self.__auth.is_refresh_token_valid():
                raise Exception('Refresh token has expired')

            ajax = self.auth_call(Request(POST, TOKEN_ENDPOINT, body={
                'grant_type': 'refresh_token',
                'refresh_token': self.__auth.get_refresh_token(),
                'access_token_ttl': ACCESS_TOKEN_TTL,
                'refresh_token_ttl': REFRESH_TOKEN_TTL_REMEMBER if self.__auth.is_remember() else REFRESH_TOKEN_TTL
            }))

            self.__auth.set_data(ajax.get_response().get_data())

            self.__auth.resume()

        else:

            while self.__auth.is_paused():
                print("Waiting for refresh\n")
                time.sleep(1)
            self.is_authorized(False)

    def api_call(self, request):
        self.is_authorized()
        request.set_header(AUTHORIZATION, self.__get_auth_header())
        request.set_url(self.api_url(request.get_url(), {'addServer': True}))
        ajax = Ajax(request)
        ajax.send()
        return ajax

    def auth_call(self, request):
        request.set_header(AUTHORIZATION, 'Basic ' + self.__get_api_key())
        request.set_header(CONTENT_TYPE, URL_ENCODED_CONTENT_TYPE)
        request.set_url(self.api_url(request.get_url(), {'addServer': True}))
        request.set_method(POST)
        ajax = Ajax(request)
        ajax.send()
        return ajax

    def __get_api_key(self):
        return base64.b64encode(self.appKey + ':' + self.appSecret)

    def __get_auth_header(self):
        return self.__auth.get_token_type() + ' ' + self.__auth.get_access_token()

    def api_url(self, url, options=None):
        built_url = ''
        options = options if options else {}

        if 'addServer' in options and options['addServer'] and url.find('http://') < 0 and url.find('https://') < 0:
            built_url += self.__server

        if url.find(URL_PREFIX) < 0:
            built_url += URL_PREFIX + '/' + API_VERSION

        if url.find(ACCOUNT_PREFIX) < 0:
            built_url = built_url.replace(ACCOUNT_PREFIX + ACCOUNT_ID, ACCOUNT_PREFIX + self.__account)

        built_url += url

        if 'addMethod' in options and options['addMethod']:
            built_url += ('&' if url.find('?') >= 0 else '?') + '_method=' + options['addMethod']

        if 'addToken' in options and options['addToken']:
            built_url += ('&' if url.find('?') >= 0 else '?') + 'access_token=' + options['addMethod']

        return built_url



