#!/usr/bin/env python
# encoding: utf-8

from .platform import Platform
from .subscription import Subscription
from .http import Client


class SDK:
    def __init__(self, key, secret, server, name='', version=''):
        self._client = Client()
        self._platform = Platform(self._client, key, secret, server, name, version)

    def platform(self):
        return self._platform

    def create_subscription(self):
        return Subscription(self._platform)