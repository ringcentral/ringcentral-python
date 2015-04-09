#!/usr/bin/env python
# encoding: utf-8

from .mock import *
from ..response import Response
from time import time
from datetime import date


class PresenceSubscriptionMock(Mock):
    def __init__(self, id='1', detailed=True):
        Mock.__init__(self)

        self._path = '/restapi/v1.0/subscription'
        self._id = id
        self._detailed = detailed

    def get_response(self, request):
        detailed = '?detailedTelephonyState=true' if self._detailed else ''
        expires_in = 15 * 60 * 60

        return Response(200, create_body({
            'eventFilters': ['/restapi/v1.0/account/~/extension/' + self._id + '/presence' + detailed],
            'expirationTime': date.fromtimestamp(time() + expires_in).isoformat(),
            'expiresIn': expires_in,
            'deliveryMode': {
                'transportType': 'PubNub',
                'encryption': True,
                'address': '123_foo',
                'subscriberKey': 'sub-c-foo',
                'secretKey': 'sec-c-bar',
                'encryptionAlgorithm': 'AES',
                'encryptionKey': 'e0bMTqmumPfFUbwzppkSbA=='
            },
            'creationTime': date.today().isoformat(),
            'id': 'foo-bar-baz',
            'status': 'Active',
            'uri': 'https://platform.ringcentral.com/restapi/v1.0/subscription/foo-bar-baz'
        }))
