# RingCentral SDK for Python

[![Build Status](https://img.shields.io/travis/ringcentral/ringcentral-python/master.svg)](https://travis-ci.org/ringcentral/ringcentral-python )

# Installation

## Manual

```sh
$ git clone https://github.com/ringcentral/python-sdk.git ./ringcentral-python-sdk
```

Install dependencies:

- [Pubnub](https://www.pubnub.com/docs/python/pubnub-python-sdk) 
- [Requests](http://docs.python-requests.org/en/latest) 

## PIP

```sh
$ pip install ringcentral
```

# Usage

For more info take a look on the `test.py` in this repository.

```py
from ringcentral import SDK

sdk = SDK('APP_KEY', 'APP_SECRET', 'SERVER')
platform = sdk.platform()
platform.login('USERNAME', 'EXTENSION', 'PASSWORD')

res = platform.get('/account/~/extension/~')
print('User loaded ' + res.json().name)
```

# Subscribing for server events

```py
from threading import Thread
from time import sleep
from ringcentral.subscription import Events

def on_message(msg):
    print(msg)

def pubnub():
    s = sdk.create_subscription()
    s.add_events(['/account/~/extension/~/message-store'])
    s.on(Events.notification, on_message)
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
```
