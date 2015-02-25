#!/usr/bin/env python
# encoding: utf-8

from .cache import Cache


class MemoryCache(Cache):
    def __init__(self):
        Cache.__init__(self)
        self.store = {}

    def save(self, key, obj):
        self.store[key] = obj
        Cache.save(self, key, obj)

    def load(self, key):
        return self.store.get(key, {})