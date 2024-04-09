# RingCentral SDK for Python

[![Build Status](https://img.shields.io/travis/ringcentral/ringcentral-python/master.svg)](https://travis-ci.org/ringcentral/ringcentral-python)
[![Coverage Status](https://coveralls.io/repos/github/ringcentral/ringcentral-python/badge.svg?branch=master)](https://coveralls.io/github/ringcentral/ringcentral-python?branch=master)
[![Twitter](https://img.shields.io/twitter/follow/ringcentraldevs.svg?style=social&label=follow)](https://twitter.com/RingCentralDevs)

__[RingCentral Developers](https://developer.ringcentral.com/api-products)__ is a cloud communications platform which can be accessed via more than 70 APIs. The platform's main capabilities include technologies that enable:
__[Voice](https://developer.ringcentral.com/api-products/voice), [SMS/MMS](https://developer.ringcentral.com/api-products/sms), [Fax](https://developer.ringcentral.com/api-products/fax), [Glip Team Messaging](https://developer.ringcentral.com/api-products/team-messaging), [Data and Configurations](https://developer.ringcentral.com/api-products/configuration)__.

[API Reference](https://developer.ringcentral.com/api-docs/latest/index.html) and [APIs Explorer](https://developer.ringcentral.com/api-explorer/latest/index.html).

## Installation

This SDK is tested against Python 3.7 so we recommend [installing using it with Python 3.7 or newer](https://www.python.org/downloads/)

```sh
$ pip3 install ringcentral
```

## Usage

Take a look at a sample code.

```py
from ringcentral import SDK

sdk = SDK('CLIENT_ID', 'CLIENT_SECRET', 'SERVER')
platform = sdk.platform()
platform.login(jwt='JWT_TOKEN')
res = platform.get('/account/~/extension/~')
print('User loaded ' + res.json().name)
```


## Subscribing for server events

Please refer to [demo_subscription.py](./ringcentral/demos/demo_subscription.py)


## Send sms
```py
from ringcentral import SDK

database = []
database.append({"Customer":"Tyler","Payment":"Due","PhoneNumber":"xxxxxxxxxxx"})
database.append({"Customer":"Chen","Payment":"Paid","PhoneNumber":"xxxxxxxxxxx"})
database.append({"Customer":"Anne","Payment":"Paid","PhoneNumber":"xxxxxxxxxxx"})
database.append({"Customer":"Brown","Payment":"Due","PhoneNumber":"xxxxxxxxxxx"})
database.append({"Customer":"Peter","Payment":"Due","PhoneNumber":"xxxxxxxxxxx"})
database.append({"Customer":"White","Payment":"Paid","PhoneNumber":"xxxxxxxxxxx"})
database.append({"Customer":"Lisa","Payment":"Paid","PhoneNumber":"xxxxxxxxxxx"})
database.append({"Customer":"Dan","Payment":"Paid","PhoneNumber":"xxxxxxxxxxx"})
database.append({"Customer":"Stephanie","Payment":"Due","PhoneNumber":"xxxxxxxxxxx"})
database.append({"Customer":"Lukas","Payment":"Due","PhoneNumber":"xxxxxxxxxxx"})

sdk = SDK('CLIENT_ID', 'CLIENT_SECRET', 'SERVER')
platform = sdk.platform()
platform.login(jwt='JWT_TOKEN')

def sendSMS(message, number):  
    params = {'from': {'phoneNumber': 'USERNAME'},'to': [{'phoneNumber': number}],'text': message}
    response = platform.post('/restapi/v1.0/account/~/extension/~/sms', params)
    print('Sent payment reminder to ' + number)

def main():
    for i in range(len(database)):
        customer = database[i]
        if customer['Payment'] is "Due":
            sendSMS("Hi " + customer['Customer'] + ". Your payment is due.", customer['PhoneNumber'])
        time.sleep(5)
    print("Send payment reminder done.")

if __name__ == '__main__':
    main()
```


## dev-notes 

https://github.com/ringcentral/ringcentral-python/blob/master/dev-notes.md
