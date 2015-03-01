# Installation

## Manual

```sh
$ git clone https://github.com/ringcentral/python-sdk.git ./ringcentral-python-sdk
```

Install dependencies:

- PUBNUB: Installation instructions: [http://www.pubnub.com/docs/python/python-sdk.html](http://www.pubnub.com/docs/python/python-sdk.html)

## PIP

```sh
$ pip install rcsdk
```

## Dependencies

Python 2.6.*

### PubNub:

Installation instructions: [http://www.pubnub.com/docs/python/python-sdk.html](http://www.pubnub.com/docs/python/python-sdk.html)

# Usage

For more info take a look on the `test.py` in this repository.

```py
from rcsdk import RCSDK
from rcsdk.core.ajax.request import Request
from rcsdk.core.cache.memorycache import MemoryCache

sdk = RCSDK(MemoryCache(), 'APP_KEY', 'APP_SECRET', 'SERVER')
platform = memory_sdk.get_platform()
platform.authorize('USERNAME', 'EXTENSION', 'PASSWORD')

call = memory_platform.api_call(Request('GET', '/account/~/extension/~'))
print('Memory User loaded ' + call.get_response().get_data()['name'])
```

# Subscribing for server events

```py
from threading import Thread
from time import sleep
from rcsdk.core.subscription.subscription import EVENTS

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
```
