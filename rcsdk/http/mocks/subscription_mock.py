#!/usr/bin/env python
# encoding: utf-8

from .mock import *
from ..response import Response
from time import time
from datetime import date


class SubscriptionMock(Mock):
    def __init__(self, expires_in=54000):
        Mock.__init__(self)

        self._path = '/restapi/v1.0/subscription'
        self._expires_in = expires_in

    def get_response(self, request):
        return Response(200, create_body({
            'eventFilters': request.get_body()['eventFilters'],
            'expirationTime': date.fromtimestamp(time() + self._expires_in).isoformat(),
            'expiresIn': self._expires_in,
            'deliveryMode': {
                'transportType': 'PubNub',
                'encryption': False,
                'address': '123_foo',
                'subscriberKey': 'sub-c-foo',
                'secretKey': 'sec-c-bar'
            },
            'id': 'foo-bar-baz',
            'creationTime': date.today().isoformat(),
            'status': 'Active',
            'uri': 'https://platform.ringcentral.com/restapi/v1.0/subscription/foo-bar-baz'
        }))
