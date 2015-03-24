#!/usr/bin/env python
# encoding: utf-8

VERSION = '0.3.0'


from .platform import Platform
from .subscription import Subscription


class RCSDK:
    def __init__(self, key, secret, server):
        self.__platform = Platform(key, secret, server)

    def get_platform(self):
        return self.__platform

    def get_subscription(self):
        return Subscription(self.__platform)
