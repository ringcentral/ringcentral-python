#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import ConfigParser

sys.path.insert(0, 'lib/')

from rcsdk import RCSDK
from core.ajax.request import Request
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

    print 'Test with memory cache'
    memory_platform = RCSDK(MemoryCache(), APP_KEY, APP_SECRET).get_platform()
    memory_platform.authorize(USERNAME, EXTENSION, PASSWORD)
    print 'Memory Authorized'
    memory_platform.refresh()
    print 'Memory Refreshed'
    call = memory_platform.api_call(Request('GET', '/account/~/extension/~'))
    print 'Memory User loaded ' + call.get_response().get_data()['name']

    print 'Test with file cache'
    cache_dir = os.path.join(os.getcwd(), '_cache')
    file_platform = RCSDK(FileCache(cache_dir), APP_KEY, APP_SECRET).get_platform()
    try:
        file_platform.is_authorized()
        print 'File is authorized already'
    except Exception, e:
        file_platform.authorize(USERNAME, EXTENSION, PASSWORD)
        print 'File Authorized'

    call = file_platform.api_call(Request('GET', '/account/~/extension/~'))
    print 'File User loaded ' + call.get_response().get_data()['name']



if __name__ == '__main__':
    main()