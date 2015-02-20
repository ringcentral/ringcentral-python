#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import ConfigParser

sys.path.insert(0, 'lib/')

from rcsdk import RCSDK
from core.cache.filecache import FileCache
from core.cache.memorycache import MemoryCache

config = ConfigParser.ConfigParser()
config.read('credentials.ini')

USERNAME = config.get('Credentials', 'USERNAME')
EXTENSION = config.get('Credentials', 'EXTENSION')
PASSWORD = config.get('Credentials', 'PASSWORD')
APP_KEY = config.get('Credentials', 'APP_KEY')
APP_SECRET = config.get('Credentials', 'APP_SECRET')


def main():
    cache_dir = os.path.join(os.getcwd(), '_cache')
    sdk_memory = RCSDK(MemoryCache(), APP_KEY, APP_SECRET)
    sdk_file = RCSDK(FileCache(cache_dir), APP_KEY, APP_SECRET)

    memory_platform = sdk_memory.get_platform()


if __name__ == '__main__':
    main()