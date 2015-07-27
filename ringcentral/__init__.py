#!/usr/bin/env python
# encoding: utf-8

from .platform import Platform
from .subscription import Subscription
from .core.context import Context


VERSION = '0.4.1'


class RCSDK:
    def __init__(self, key, secret, server):
        self.__context = Context()
        self.__platform = Platform(self.__context, key, secret, server)

    def get_platform(self):
        return self.__platform

    def get_subscription(self):
        return Subscription(self.__context, self.__platform)

    def get_context(self):
        return self.__context