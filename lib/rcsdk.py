#!/usr/bin/env python
# encoding: utf-8

from core.platform.platform import Platform


class RCSDK:
    def __init__(self, cache, key, secret):
        self.__platform = Platform(cache, key, secret)

    def get_platform(self):
        return self.__platform