#!/usr/bin/env python
# encoding: utf-8

from multiprocessing import Process
from time import sleep
from ringcentral.subscription import Events
from ringcentral import SDK
from config import USERNAME, EXTENSION, PASSWORD, APP_KEY, APP_SECRET, SERVER


def main():
    sdk = SDK(APP_KEY, APP_SECRET, SERVER)
    platform = sdk.platform()
    platform.login(USERNAME, EXTENSION, PASSWORD)

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

    print("Wait for notification...")


if __name__ == '__main__':
    main()