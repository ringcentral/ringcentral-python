#!/usr/bin/env python
# encoding: utf-8

from pubnub import Pubnub
from .mock import PubnubMock


class PubnubFactory:
    def __init__(self, use_mock):
        self._use_mock = use_mock

    def pubnub(self, subscribe_key, ssl_on=False, publish_key=''):
        if self._use_mock:
            return PubnubMock()
        else:
            return Pubnub(subscribe_key=subscribe_key, ssl_on=ssl_on, publish_key=publish_key)
