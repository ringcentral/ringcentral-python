#!/usr/bin/env python
# encoding: utf-8

from ..http.mocks.mocks import Mocks
from ..http.request import Request
from ..subscription.pubnub_mock import PubnubMock
from ..http.request_mock import RequestMock

class Context:
    def __init__(self):
        self.__usePubnubMock = False
        self.__useRequestMock = False
        self.__mocks = Mocks()

    def get_pubnub(self, subscribe_key, ssl_on=False, publish_key=''):
        if self.__usePubnubMock:
            return PubnubMock()
        else:
            from Pubnub import Pubnub
            return Pubnub(subscribe_key=subscribe_key, ssl_on=ssl_on, publish_key=publish_key)

    def get_request(self, method, url, query_params=None, body=None, headers=None):
        if self.__useRequestMock:
            return RequestMock(self.get_mocks(), method, url, query_params, body, headers)
        else:
            return Request(method, url, query_params, body, headers)

    def use_pubnub_stub(self, flag):
        self.__usePubnubMock = flag
        return self

    def use_request_stub(self, flag):
        self.__useRequestMock = flag
        return self

    def get_mocks(self):
        return self.__mocks