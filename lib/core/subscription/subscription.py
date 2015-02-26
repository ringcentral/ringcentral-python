#!/usr/bin/env python
# encoding: utf-8
import base64
from threading import Timer

from Pubnub import Pubnub
from Pubnub import AES

from core.ajax.request import *


EVENTS = {
    'notification': 'notification',
    'removeSuccess': 'removeSuccess',
    'removeError': 'removeError',
    'renewSuccess': 'renewSuccess',
    'renewError': 'renewError',
    'subscribeSuccess': 'subscribeSuccess',
    'subscribeError': 'subscribeError'
}

RENEW_HANDICAP = 60


class Subscription:
    def __init__(self, platform):
        self.__platform = platform
        self.__event_filters = []
        self.__timeout = None
        self.__subscription = {
            'eventFilters': [],
            'expirationTime': '',  # 2014-03-12T19:54:35.613Z
            'expiresIn': 0,
            'deliveryMode': {
                'transportType': 'PubNub',
                'encryption': False,
                'address': '',
                'subscriberKey': '',
                'secretKey': ''
            },
            'id': '',
            'creationTime': '',  # 2014-03-12T19:54:35.613Z
            'status': '',  # Active
            'uri': ''
        }
        self.__pubnub = None
        self.__listeners = {}

    def on(self, event, fn):
        if event not in self.__listeners:
            self.__listeners[event] = []
        self.__listeners[event].append(fn)

    def __emit(self, event, data=None):
        if event in self.__listeners:
            for l in self.__listeners[event]:
                l(data)

    def register(self, options):
        if self.is_subscribed():
            self.renew(options)
        else:
            self.register(options)

    def add_events(self, events):
        self.__event_filters += events

    def set_events(self, events):
        self.__event_filters = events

    def subscribe(self, options=None):
        options = options if options else {}
        self.__event_filters = options['events'] if 'events' in options else []
        try:
            if not self.__event_filters or len(self.__event_filters) == 0:
                raise Exception('Events are undefined')
            body = {
                'eventFilters': self.__get_full_events_filter(),
                'deliveryMode': {
                    'transportType': 'PubNub'
                }
            }
            req = Request(POST, '/restapi/v1.0/subscription', body=body)
            ajax = self.__platform.api_call(req)
            data = ajax.get_response().get_data()
            self.__update_subscription(data)
            self.__subscribe_at_pubnub()
            self.__emit(EVENTS['subscribeSuccess'], data)
        except Exception, e:
            self.un_subscribe()
            self.__emit(EVENTS['subscribeError'], e)

    def renew(self, options):
        options = options if options else {}
        self.__event_filters = options['events'] if 'events' in options else []
        self.__clear_timeout()
        try:
            if not self.__subscription or ('id' not in self.__subscription) or not self.__subscription['id']:
                raise Exception('Subscription ID is required')
            if not self.__event_filters or len(self.__event_filters) == 0:
                raise Exception('Events are undefined')
            body = {
                'eventFilters': self.__get_full_events_filter()
            }
            req = Request(PUT, '/restapi/v1.0/subscription' + self.__subscription['id'], body=body)
            ajax = self.__platform.api_call(req)
            data = ajax.get_response().get_data()
            self.__update_subscription(data)
            self.__emit(EVENTS['subscribeSuccess'], data)
        except Exception, e:
            self.un_subscribe()
            self.__emit(EVENTS['renewError'], e)

    def remove(self):
        try:
            if not self.__subscription or ('id' not in self.__subscription) or not self.__subscription['id']:
                raise Exception('Subscription ID is required')
            req = Request(DELETE, '/restapi/v1.0/subscription' + self.__subscription['id'])
            self.__platform.api_call(req)
            self.un_subscribe()
            self.__emit(EVENTS['removeSuccess'])
        except Exception, e:
            self.un_subscribe()
            self.__emit(EVENTS['removeError'], e)

    def destroy(self):
        self.un_subscribe()

    def un_subscribe(self):
        self.__clear_timeout()
        self.__un_subscribe_at_pubnub()
        self.__subscription = None

    def is_subscribed(self):
        with self.__subscription as s:
            return s['deliveryMode'] and s['deliveryMode']['subscribeKey'] and s['deliveryMode']['address']

    def __update_subscription(self, data):
        self.__clear_timeout()
        self.__subscription = data
        self.__set_timeout()

    def __subscribe_at_pubnub(self):
        if not self.is_subscribed():
            return
        # TODO check this stuff
        self.__pubnub = Pubnub(subscribe_key=self.__subscription['deliveryMode']['subscriberKey'], ssl_on=False)

        def callback(message, channel):
            key = base64.b64decode(self.__subscription['deliveryMode']['encryptionKey'])
            data = base64.b64decode(message)
            obj2 = AES.new(key, AES.MODE_ECB, 'This is an IV456')
            decrypted = obj2.decrypt(data)
            print(decrypted)

        def error(message):
            print("ERROR : " + str(message))

        def connect(message):
            print("CONNECTED")

        def reconnect(message):
            print("RECONNECTED")

        def disconnect(message):
            print("DISCONNECTED")

            self.__pubnub.subscribe(self.__subscription['deliveryMode']['address'], callback=callback, error=callback,
                                    connect=connect, reconnect=reconnect, disconnect=disconnect)

    def __notify(self, message):
        if self.is_subscribed() and self.__subscription['deliveryMode']['encriptionKey']:
            pass  # TODO decrypt AES
        self.__emit(EVENTS['notification'], message)

    def __un_subscribe_at_pubnub(self):
        if self.__pubnub and self.is_subscribed():
            pass  # TODO disconnect from PUBNUB

    def __get_full_events_filter(self):
        return [self.__platform.api_url(e) for e in self.__event_filters]

    def __set_timeout(self):
        time_to_expiration = self.__subscription['expiresIn'] - RENEW_HANDICAP
        self.__timeout = Timer(time_to_expiration, self.renew)
        self.__timeout.start()

    def __clear_timeout(self):
        if self.__timeout:
            self.__timeout.cancel()


if __name__ == '__main__':
    pass