#!/usr/bin/env python
# encoding: utf-8

import urllib
from config import USERNAME, EXTENSION, PASSWORD, APP_KEY, APP_SECRET, SERVER, MOBILE
from ringcentral import SDK


def main():
    sdk = SDK(APP_KEY, APP_SECRET, SERVER)
    platform = sdk.platform()
    platform.login(USERNAME, EXTENSION, PASSWORD)

    to_numbers = "1234567890"

    params = {'from': {'phoneNumber': USERNAME},'to': [{'phoneNumber': to_number}],'text': "SMS message"}
    response = platform.post('/restapi/v1.0/account/~/extension/~/sms', params)

    print 'Sent SMS: ' + response.json().uri

if __name__ == '__main__':
    main()
