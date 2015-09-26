#!/usr/bin/env python
# encoding: utf-8

from time import time

RELEASE_TIMEOUT = 10


class Auth:
    def __init__(self):
        self.__remember = False

        self.__token_type = ''

        self.__access_token = ''
        self.__expires_in = 0
        self.__expire_time = 0

        self.__refresh_token = ''
        self.__refresh_token_expires_in = 0
        self.__refresh_token_expire_time = 0

        self.__scope = ''
        self.__owner_id = ''

    def set_data(self, auth_data=None):

        if auth_data is None:
            return self

        # Misc

        if 'remeber' in auth_data:
            self.__remember = auth_data.get('remember')

        if 'token_type' in auth_data:
            self.__token_type = auth_data.get('token_type')

        if 'owner_id' in auth_data:
            self.__owner_id = auth_data.get('owner_id')

        if 'scope' in auth_data:
            self.__scope = auth_data.get('scope')

        # Access Token

        if 'access_token' in auth_data:
            self.__access_token = auth_data.get('access_token')

        if 'expires_in' in auth_data:
            self.__expires_in = auth_data.get('expires_in')

        if 'expire_time' not in auth_data and 'expires_in' in auth_data:
            self.__expire_time = time() + auth_data.get('expires_in')
        elif 'expire_time' in auth_data:
            self.__expire_time = auth_data.get('expire_time')

        # Refresh Token

        if 'refresh_token' in auth_data:
            self.__refresh_token = auth_data.get('refresh_token')

        if 'refresh_token_expires_in' in auth_data:
            self.__refresh_token_expires_in = auth_data.get('refresh_token_expires_in')

        if 'refresh_token_expire_time' not in auth_data and 'refresh_token_expires_in' in auth_data:
            self.__refresh_token_expire_time = time() + auth_data.get('refresh_token_expires_in')
        elif 'refresh_token_expire_time' in auth_data:
            self.__refresh_token_expire_time = auth_data.get('refresh_token_expire_time')

        return self

    def data(self):
        return {
            'remember': self.__remember,
            'token_type': self.__token_type,

            'access_token': self.__access_token,
            'expires_in': self.__expires_in,
            'expire_time': self.__expire_time,

            'refresh_token': self.__refresh_token,
            'refresh_token_expires_in': self.__refresh_token_expires_in,
            'refresh_token_expire_time': self.__refresh_token_expire_time,

            'scope': self.__scope,
            'owner_id': self.__owner_id
        }

    def reset(self):
        self.__remember = False

        self.__token_type = ''

        self.__access_token = ''
        self.__expires_in = 0
        self.__expire_time = 0

        self.__refresh_token = ''
        self.__refresh_token_expires_in = 0
        self.__refresh_token_expire_time = 0

        self.__scope = ''
        self.__owner_id = ''

    def access_token(self):
        return self.__access_token

    def refresh_token(self):
        return self.__refresh_token

    def token_type(self):
        return self.__token_type

    def access_token_valid(self):
        return self.__is_token_date_valid(self.data().get('expire_time'))

    def refresh_token_valid(self):
        return self.__is_token_date_valid(self.data().get('refresh_token_expire_time'))

    @staticmethod
    def __is_token_date_valid(token_date):
        return token_date > time()