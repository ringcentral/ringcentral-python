#!/usr/bin/env python
# encoding: utf-8

import base64

from core.platform.auth import Auth


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
        self.server = server if server else SERVER
        self.appKey = key
        self.appSecret = secret
        self.__auth = Auth(cache)
        self.__account = ACCOUNT_ID

    def is_authorized(self, refresh=True):
        if not self.__auth.is_access_token_valid() and refresh:
            self.refresh()
        if not self.__auth.is_access_token_valid():
            raise Exception('Access token is not valid after refresh timeout')

    def get_api_key(self):
        return base64.b64decode(self.appKey + ':' + self.appSecret)

    def get_auth_header(self):
        return self.__auth.get_token_type() + ' ' + self.__auth.get_access_token()

    def authorize(self):
        pass

    def refresh(self):
        pass

    def api_call(self):
        pass

    def auth_call(self):
        pass

    def __get_auth_header(self):
        pass

    def __api_url(self):
        pass

