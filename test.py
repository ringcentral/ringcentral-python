#!/usr/bin/env python
# encoding: utf-8

import os
import json
import ConfigParser

from rcsdk import RCSDK
from rcsdk.http.request import Request


config = ConfigParser.ConfigParser()
config.read('credentials.ini')

USERNAME = config.get('Credentials', 'USERNAME')
EXTENSION = config.get('Credentials', 'EXTENSION')
PASSWORD = config.get('Credentials', 'PASSWORD')
APP_KEY = config.get('Credentials', 'APP_KEY')
APP_SECRET = config.get('Credentials', 'APP_SECRET')
SERVER = config.get('Credentials', 'SERVER')

cache_dir = os.path.join(os.getcwd(), '_cache')
file_path = os.path.join(cache_dir, 'platform.json')


def get_file_cache():
    try:
        f = open(file_path, 'r')
        data = json.load(f)
        f.close()
        return data if data else {}
    except IOError:
        return {}


def set_file_cache(cache):
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)
    f = open(file_path, 'w')
    json.dump(cache, f, indent=4)
    f.close()


def main():
    cache = get_file_cache()

    # Create SDK instance
    sdk = RCSDK(APP_KEY, APP_SECRET, SERVER)
    platform = sdk.get_platform()

    # Set cached authentication data
    platform.set_auth_data(cache)

    # Check authentication
    try:
        platform.is_authorized()
        print('Authorized already by cached data')
    except Exception as e:
        platform.authorize(USERNAME, EXTENSION, PASSWORD)
        print('Authorized by credentials')

    # Perform refresh by force
    platform.refresh()
    print('Refreshed')

    user = platform.api_call(Request('GET', '/account/~/extension/~'))
    print('User loaded ' + user.get_data()['name'])

    #multipart_response = platform.api_call(Request('GET', '/account/~/extension/~/message-store/' + str(user.get_data()['id']) + ',' + str(user.get_data()['id'])))
    #print 'Memory messages loaded ' + " ".join([str(r.get_data()['id']) for r in multipart_response.get_responses()])

    # Pubnub notifications example
    # def on_message(msg):
    #     print(msg)
    #
    # def pubnub():
    #     s = sdk.get_subscription()
    #     s.add_events(['/account/~/extension/~/message-store'])
    #     s.on(EVENTS['notification'], on_message)
    #     s.register()
    #     while True:
    #         sleep(0.1)
    #
    # try:
    #     try:
    #         import Pubnub
    #         t = Thread(target=pubnub)
    #         t.start()
    #     except ImportError as e:
    #         print("No Pubnub SDK, skipping Pubnub test")
    # except KeyboardInterrupt:
    #     raise Exception('Stopped by user')

    set_file_cache(platform.get_auth_data())
    print("Authentication data has been cached")

    print("Wait for notification...")


if __name__ == '__main__':
    main()