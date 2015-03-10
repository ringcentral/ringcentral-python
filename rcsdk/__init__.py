#!/usr/bin/env python
# encoding: utf-8

VERSION = '0.2.4'


from .platform import Platform
from .platform.client import Client
from .subscription import Subscription


class RCSDK:
    def __init__(self, key, secret, server):
        self.__platform = Platform(key, secret, server)
        self.__client = Client(self.__platform)

    def get_platform(self):
        return self.__platform

    def get_client(self):
        return self.__client

    def get_subscription(self):
        return Subscription(self.__platform)
