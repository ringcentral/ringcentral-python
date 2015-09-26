#!/usr/bin/env python
# encoding: utf-8

from .platform import Platform
from .subscription import Subscription
from .mocks import Registry
from .mocks import Client as MockClient
from .http import Client as HttpClient
from .pubnub import PubnubFactory


class SDK:
    def __init__(self, key, secret, server, name='', version='', use_http_mock=False, use_pubnub_mock=False):
        self._registry = Registry()
        self._client = HttpClient() if not use_http_mock else MockClient(self._registry)
        self._pubnub_factory = PubnubFactory(use_pubnub_mock)
        self._platform = Platform(self._client, key, secret, server, name, version)

    def mock_registry(self):
        return self._registry

    def platform(self):
        return self._platform

    def create_subscription(self):
        return Subscription(self._platform, self._pubnub_factory)