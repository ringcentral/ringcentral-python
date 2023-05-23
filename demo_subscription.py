from multiprocessing import Process
from time import sleep
from ringcentral.subscription import Events
from ringcentral import SDK
from dotenv import dotenv_values

#from config import USERNAME, EXTENSION, PASSWORD, APP_KEY, APP_SECRET, SERVER

env = dotenv_values(".env")

def main():
    sdk = SDK(env['RINGCENTRAL_CLIENT_ID'], env['RINGCENTRAL_CLIENT_SECRET'], env['RINGCENTRAL_SERVER_URL'])
    platform = sdk.platform()
    platform.login(jwt = env['RINGCENTRAL_JWT_TOKEN'])

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
