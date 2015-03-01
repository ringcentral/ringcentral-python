#!/usr/bin/env python
# encoding: utf-8

VERSION = '0.2.4'


from core.platform.platform import Platform
from core.subscription.subscription import Subscription

class RCSDK:
    def __init__(self, cache, key, secret, server):
        self.__platform = Platform(cache, key, secret, server)

    def get_platform(self):
        return self.__platform

    def get_subscription(self):
        return Subscription(self.__platform)
