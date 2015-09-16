#!/usr/bin/env python
# encoding: utf-8

import base64
import sys
from .auth import Auth

ACCOUNT_ID = '~'
ACCOUNT_PREFIX = '/account/'
URL_PREFIX = '/restapi'
TOKEN_ENDPOINT = '/restapi/oauth/token'
REVOKE_ENDPOINT = '/restapi/oauth/revoke'
API_VERSION = 'v1.0'
ACCESS_TOKEN_TTL = 3600  # 60 minutes
REFRESH_TOKEN_TTL = 604800  # 1 week


class Platform:
    def __init__(self, client, key='', secret='', server='', name='', version=''):
        self._server = server
        self._key = key
        self._name = name if name else 'Unnamed'
        self._version = version if version else '0.0.0'
        self._secret = secret
        self._client = client
        self._auth = Auth()
        self._account = ACCOUNT_ID
        self._userAgent = ((self._name + ('/' + self._version if self._version else '') + ' ') if self._name else '') + \
                          sys.platform + '/VERSION' + ' ' + \
                          'PYTHON/VERSION ' + \
                          'RCPYTHONSDK/VERSION'

    def auth(self):
        return self._auth

    def create_url(self, url, add_server=False, add_method=None, add_token=False):
        built_url = ''
        has_http = url.find('http://') >= 0 or url.find('https://') >= 0

        if add_server and not has_http:
            built_url += self._server

        if url.find(URL_PREFIX) < 0 and not has_http:
            built_url += URL_PREFIX + '/' + API_VERSION

        if url.find(ACCOUNT_PREFIX) >= 0:
            built_url = built_url.replace(ACCOUNT_PREFIX + ACCOUNT_ID, ACCOUNT_PREFIX + self._account)

        built_url += url

        if add_method:
            built_url += ('&' if built_url.find('?') >= 0 else '?') + '_method=' + add_method

        if add_token:
            built_url += ('&' if built_url.find('?') >= 0 else '?') + 'access_token=' + self._auth.access_token()

        return built_url

    def logged_in(self):
        try:
            return True if self._auth.access_token_valid() or self.refresh() else False
        except:
            return False

    def login(self, username, extension, password):
        response = self._request_token(TOKEN_ENDPOINT, body={
            'grant_type': 'password',
            'username': username,
            'extension': extension,
            'password': password,
            'access_token_ttl': ACCESS_TOKEN_TTL,
            'refresh_token_ttl': REFRESH_TOKEN_TTL
        })
        self._auth.set_data(response.json_dict())
        return response

    def refresh(self):
        if not self._auth.refresh_token_valid():
            raise Exception('Refresh token has expired')

        response = self._request_token(TOKEN_ENDPOINT, body={
            'grant_type': 'refresh_token',
            'refresh_token': self._auth.refresh_token(),
            'access_token_ttl': ACCESS_TOKEN_TTL,
            'refresh_token_ttl': REFRESH_TOKEN_TTL
        })

        self._auth.set_data(response.json_dict())

        return response

    def logout(self):
        response = self._request_token(REVOKE_ENDPOINT, body={
            'token': self._auth.access_token()
        })
        self._auth.reset()
        return response

    def inflate_request(self, request, skip_auth_check=False):
        if not skip_auth_check:
            self._ensure_authentication()
            request.headers['Authorization'] = self._auth_header()

        request.headers['User-Agent'] = self._userAgent
        request.headers['RC-User-Agent'] = self._userAgent
        request.url = self.create_url(request.url, add_server=True)

        return request

    def send_request(self, request, skip_auth_check=False):
        return self._client.send(self.inflate_request(request, skip_auth_check=skip_auth_check))

    def get(self, url, query_params=None, headers=None, skip_auth_check=False):
        request = self._client.create_request('GET', url, query_params=query_params, headers=headers)
        return self.send_request(request, skip_auth_check=skip_auth_check)

    def post(self, url, body=None, query_params=None, headers=None, skip_auth_check=False):
        request = self._client.create_request('POST', url, query_params=query_params, headers=headers, body=body)
        return self.send_request(request, skip_auth_check=skip_auth_check)

    def put(self, url, body=None, query_params=None, headers=None, skip_auth_check=False):
        request = self._client.create_request('PUT', url, query_params=query_params, headers=headers, body=body)
        return self.send_request(request, skip_auth_check=skip_auth_check)

    def delete(self, url, query_params=None, headers=None, skip_auth_check=False):
        request = self._client.create_request('DELETE', url, query_params=query_params, headers=headers)
        return self.send_request(request, skip_auth_check=skip_auth_check)

    def _request_token(self, path='', body=None):
        headers = {
            'Authorization': 'Basic ' + self._api_key(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        request = self._client.create_request('POST', path, body=body, headers=headers)
        return self.send_request(request, skip_auth_check=True)

    def _api_key(self):
        return base64.b64encode(self._key + ':' + self._secret)

    def _auth_header(self):
        return self._auth.token_type() + ' ' + self._auth.access_token()

    def _ensure_authentication(self):
        if not self._auth.access_token_valid():
            self.refresh()
