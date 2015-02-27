#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import ConfigParser
from threading import Thread
from time import sleep

sys.path.insert(0, 'rcsdk/')

from rcsdk import RCSDK
from core.ajax.request import Request
from core.cache.filecache import FileCache
from core.cache.memorycache import MemoryCache
from core.subscription.subscription import EVENTS

config = ConfigParser.ConfigParser()
config.read('credentials.ini')

USERNAME = config.get('Credentials', 'USERNAME')
EXTENSION = config.get('Credentials', 'EXTENSION')
PASSWORD = config.get('Credentials', 'PASSWORD')
APP_KEY = config.get('Credentials', 'APP_KEY')
APP_SECRET = config.get('Credentials', 'APP_SECRET')


def main():
    print('Test with memory cache')
    memory_sdk = RCSDK(MemoryCache(), APP_KEY, APP_SECRET)
    memory_platform = memory_sdk.get_platform()
    memory_platform.authorize(USERNAME, EXTENSION, PASSWORD)
    print('Memory Authorized')
    memory_platform.refresh()
    print('Memory Refreshed')
    call = memory_platform.api_call(Request('GET', '/account/~/extension/~'))
    print('Memory User loaded ' + call.get_response().get_data()['name'])

    # call = memory_platform.api_call(Request('GET', '/account/~/extension/~/message-store/527975372020,527966621020,527965464020'))
    # print 'Memory messages loaded ' + " ".join([str(r.get_data()["uri"]) for r in call.get_response().get_responses()])
    #
    print('Test with file cache')
    cache_dir = os.path.join(os.getcwd(), '_cache')
    file_platform = RCSDK(FileCache(cache_dir), APP_KEY, APP_SECRET).get_platform()
    try:
        file_platform.is_authorized()
        print('File is authorized already')
    except Exception as e:
        file_platform.authorize(USERNAME, EXTENSION, PASSWORD)
        print('File Authorized')

    call = file_platform.api_call(Request('GET', '/account/~/extension/~'))
    print('File User loaded ' + call.get_response().get_data()['name'])

    def on_message(msg):
        print(msg)

    def pubnub():
        s = memory_sdk.get_subscription()
        s.add_events(['/account/~/extension/~/message-store'])
        s.on(EVENTS['notification'], on_message)
        s.register()
        while True:
            sleep(0.1)

    try:
        try:
            import Pubnub
            t = Thread(target=pubnub)
            t.start()
        except ImportError as e:
            print("No Pubnub SDK, skipping Pubnub test")
    except KeyboardInterrupt:
        pass

    print("Wait for notification...")


if __name__ == '__main__':
    main()