#!/usr/bin/env python
# encoding: utf-8

import os
import json

from core.cache.cache import Cache


class FileCache(Cache):
    def __init__(self, cache_dir):
        Cache.__init__(self)
        self.cache_dir = cache_dir

    def save(self, key, obj):
        if not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)
        f = open(self._file_path(key + '.json'), 'w')
        json.dump(obj, f, indent=4)
        f.close()
        Cache.save(self, key, obj)

    def load(self, key):
        f = open(self._file_path(key + '.json'), 'r')
        data = json.load(f)
        f.close()
        return data if data else {}

    def _file_path(self, name):
        return os.path.join(self.cache_dir, name)