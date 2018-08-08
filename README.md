# RingCentral SDK for Python

[![Build Status](https://img.shields.io/travis/ringcentral/ringcentral-python/master.svg)](https://travis-ci.org/ringcentral/ringcentral-python)
[![Coverage Status](https://coveralls.io/repos/github/ringcentral/ringcentral-python/badge.svg?branch=master)](https://coveralls.io/github/ringcentral/ringcentral-python?branch=master)
[![Community](https://img.shields.io/badge/dynamic/json.svg?label=community&colorB=&suffix=%20users&query=$.approximate_people_count&uri=http%3A%2F%2Fapi.getsatisfaction.com%2Fcompanies%2F102909.json)](https://devcommunity.ringcentral.com/ringcentraldev)
[![Twitter](https://img.shields.io/twitter/follow/ringcentraldevs.svg?style=social&label=follow)](https://twitter.com/RingCentralDevs)

__[RingCentral Developers](https://developer.ringcentral.com/api-products)__ is a cloud communications platform which can be accessed via more than 70 APIs. The platform's main capabilities include technologies that enable:
__[Voice](https://developer.ringcentral.com/api-products/voice), [SMS/MMS](https://developer.ringcentral.com/api-products/sms), [Fax](https://developer.ringcentral.com/api-products/fax), [Glip Team Messaging](https://developer.ringcentral.com/api-products/team-messaging), [Data and Configurations](https://developer.ringcentral.com/api-products/configuration)__.

[API Reference](https://developer.ringcentral.com/api-docs/latest/index.html) and [APIs Explorer](https://developer.ringcentral.com/api-explorer/latest/index.html).

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

sdk = SDK('CLIENT_ID', 'CLIENT_SECRET', 'SERVER')
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
