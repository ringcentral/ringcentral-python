#!/usr/bin/env python
# encoding: utf-8

import os
import json
from ringcentral import SDK
from config import USERNAME, EXTENSION, PASSWORD, APP_KEY, APP_SECRET, SERVER

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
    sdk = SDK(APP_KEY, APP_SECRET, SERVER)
    platform = sdk.platform()

    # Set cached authentication data
    platform.auth().set_data(cache)

    try:
        platform.is_authorized()
        print('Authorized already by cached data')
    except Exception as e:
        platform.login(USERNAME, EXTENSION, PASSWORD)
        print('Authorized by credentials')

    # Perform refresh by force
    platform.refresh()
    print('Refreshed')

    set_file_cache(platform.auth().data())
    print("Authentication data has been cached")

if __name__ == '__main__':
    main()