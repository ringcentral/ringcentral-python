#!/usr/bin/env python
# encoding: utf-8

from time import time


RELEASE_TIMEOUT = 10
CACHE_KEY = 'platform'

DEFAULT_AUTH_DATA = {
    'paused_time': 0,
    'token_type': '',
    'access_token': '',
    'expires_in': 0,
    'expire_time': 0,
    'refresh_token': '',
    'refresh_token_expires_in': 0
}


class Auth:
    def __init__(self, cache):
        self._cache = cache

    def set_data(self, auth_data=None):
        merged_data = dict(DEFAULT_AUTH_DATA.items())
        merged_data.update(self.get_data())
        merged_data.update(auth_data)

        if auth_data.get('expires_in') and not auth_data.get('expire_time'):
            merged_data['expire_time'] = time() + auth_data.get('expires_in')

        if auth_data.get('refresh_token_expires_in') and not auth_data.get('refresh_token_expire_time'):
            merged_data['refresh_token_expire_time'] = time() + auth_data.get('refresh_token_expires_in')

        self._cache.save(CACHE_KEY, merged_data)

    def get_data(self):
        cached = self._cache.load(CACHE_KEY)
        return cached if cached else {}

    def get_access_token(self):
        return self.get_data().get('access_token')

    def get_refresh_token(self):
        return self.get_data().get('refresh_token')

    def get_token_type(self):
        return self.get_data().get('token_type')

    def is_access_token_valid(self):
        return self.__is_token_date_valid(self.get_data().get('expire_time'))

    def is_refresh_token_valid(self):
        return self.__is_token_date_valid(self.get_data().get('refresh_token_expire_time'))

    def is_paused(self):
        pt = self.get_data().get('paused_time')
        return pt > 0 and (time() - pt) < RELEASE_TIMEOUT

    def pause(self):
        self.set_data({'paused_time': time()})

    def resume(self):
        self.set_data({'paused_time': 0})

    def set_remember(self, val):
        self.set_data({'remember': True if val else False})

    def is_remember(self):
        return self.get_data().get('remember', False)

    @staticmethod
    def __is_token_date_valid(token_date):
        return token_date > time()