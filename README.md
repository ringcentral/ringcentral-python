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

## Test of usage

Create a file __credentials.ini__ in the root of project with your credentials:

    [Credentials]
    USERNAME: 15554443322
    EXTENSION: 101
    PASSWORD: mypass
    APP_KEY: 11111111111111111111111111111111
    APP_SECRET: 11111111111111111111111111111111

start:

    python test.py