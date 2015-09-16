#!/usr/bin/env python
# encoding: utf-8

import os
import json
import ConfigParser
from multiprocessing import Process
from time import sleep
from ringcentral.subscription import Events
from ringcentral.http.api_exception import ApiException
from ringcentral import SDK


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
    sdk = SDK(APP_KEY, APP_SECRET, SERVER)
    platform = sdk.platform()

    # Set cached authentication data
    platform.auth().set_data(cache)

    # Check authentication
    try:
        platform.is_authorized()
        print('Authorized already by cached data')
    except Exception as e:
        platform.login(USERNAME, EXTENSION, PASSWORD)
        print('Authorized by credentials')

    # Perform refresh by force
    platform.refresh()
    print('Refreshed')

    # Simple GET
    response = platform.get('/account/~/extension/~')
    user = response.json()
    user_id = str(user.id)
    print('User loaded ' + user.name + ' (' + user_id + ')')
    print('Headers ' + str(response.response().headers))

    # Multipart response
    try:
        multipart_response = platform.get('/account/~/extension/' + user_id + ',' + user_id + '/presence').multipart()
        print 'Multipart 1\n' + str(multipart_response[0].json_dict())
        print 'Multipart 2\n' + str(multipart_response[1].json_dict())
    except ApiException as e:
        print 'Cannot load multipart'
        print 'URL ' + e.api_response().request().url
        print 'Response' + str(e.api_response().json())

    # Pubnub notifications example
    def on_message(msg):
        print(msg)

    def pubnub():
        try:
            s = sdk.create_subscription()
            s.add_events(['/account/~/extension/~/message-store'])
            s.on(Events.notification, on_message)
            s.register()

            while True:
                sleep(0.1)

        except KeyboardInterrupt:
            print("Pubnub listener stopped...")

    p = Process(target=pubnub)
    try:
        p.start()
    except KeyboardInterrupt:
        p.terminate()
        print("Stopped by User")

    set_file_cache(platform.auth().data())
    print("Authentication data has been cached")

    print("Wait for notification...")


if __name__ == '__main__':
    main()