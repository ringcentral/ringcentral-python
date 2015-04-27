#!/usr/bin/env python
# encoding: utf-8
import base64
from threading import Timer
import json
from ..http.request import *
from ..core.observable import Observable

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


class Subscription(Observable):
    def __init__(self, context, platform):
        Observable.__init__(self)
        self.__context = context
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

    def register(self, events=None):
        if self.is_subscribed():
            return self.renew(events=events)
        else:
            return self.subscribe(events=events)

    def add_events(self, events):
        self.__event_filters += events
        pass

    def set_events(self, events):
        self.__event_filters = events

    def subscribe(self, events=None):

        if events:
            self.set_events(events)

        try:
            if not self.__event_filters or len(self.__event_filters) == 0:
                raise Exception('Events are undefined')

            body = {
                'eventFilters': self.__get_full_events_filter(),
                'deliveryMode': {
                    'transportType': 'PubNub'
                }
            }
            response = self.__platform.post('/restapi/v1.0/subscription', body=body)

            data = response.get_json(False)

            self.__update_subscription(data)
            self.__subscribe_at_pubnub()
            self.emit(EVENTS['subscribeSuccess'], data)

            return response

        except Exception as e:
            self.un_subscribe()
            self.emit(EVENTS['subscribeError'], e)
            raise e

    def renew(self, events=None):

        if events:
            self.set_events(events)

        self.__clear_timeout()

        try:
            if not self.__subscription or ('id' not in self.__subscription) or not self.__subscription['id']:
                raise Exception('Subscription ID is required')

            if not self.__event_filters or len(self.__event_filters) == 0:
                raise Exception('Events are undefined')

            body = {'eventFilters': self.__get_full_events_filter()}
            response = self.__platform.put('/restapi/v1.0/subscription' + self.__subscription['id'], body=body)

            data = response.get_data(False)

            self.__update_subscription(data)
            self.emit(EVENTS['subscribeSuccess'], data)

            return response

        except Exception as e:
            self.un_subscribe()
            self.emit(EVENTS['renewError'], e)

    def remove(self):
        try:
            if not self.__subscription or ('id' not in self.__subscription) or not self.__subscription['id']:
                raise Exception('Subscription ID is required')

            response = self.__platform.delete('/restapi/v1.0/subscription' + self.__subscription['id'])

            self.un_subscribe()
            self.emit(EVENTS['removeSuccess'])

            return response

        except Exception as e:
            self.un_subscribe()
            self.emit(EVENTS['removeError'], e)

    def destroy(self):
        self.un_subscribe()
        self.off()

    def un_subscribe(self):
        self.__clear_timeout()
        self.__un_subscribe_at_pubnub()
        self.__subscription = None

    def is_subscribed(self):
        s = self.__subscription
        return ('deliveryMode' in s and s['deliveryMode']) and \
               ('subscriberKey' in s['deliveryMode'] and s['deliveryMode']['subscriberKey']) and \
               ('address' in s['deliveryMode'] and s['deliveryMode']['address'])

    def __update_subscription(self, data):
        self.__clear_timeout()
        self.__subscription = data
        self.__set_timeout()

    def __subscribe_at_pubnub(self):
        from Pubnub import Pubnub, AES

        if not self.is_subscribed():
            return

        # TODO check this stuff
        s_key = self.__subscription['deliveryMode']['subscriberKey']
        self.__pubnub = self.__context.get_pubnub(subscribe_key=s_key, ssl_on=False, publish_key='')

        def callback(message, channel=''):

            is_subscibed = self.is_subscribed()
            delivery_mode = self.__subscription['deliveryMode'] if is_subscibed else {}
            is_encrypted = ('encryption' in delivery_mode) and ('encryptionKey' in delivery_mode)

            if is_subscibed and is_encrypted:
                key = base64.b64decode(self.__subscription['deliveryMode']['encryptionKey'])
                data = base64.b64decode(message)
                obj2 = AES.new(key)
                decrypted = str(obj2.decrypt(data)).replace('\x05', '')
                self.__notify(json.loads(decrypted))
            else:
                self.__notify(message)

        def error(message):
            print("ERROR : " + str(message))

        def connect(message):
            print("CONNECTED")

        def reconnect(message):
            print("RECONNECTED")

        def disconnect(message):
            print("DISCONNECTED")

        self.__pubnub.subscribe(self.__subscription['deliveryMode']['address'], callback=callback, error=error,
                                connect=connect, reconnect=reconnect, disconnect=disconnect)

    def __notify(self, message):
        self.emit(EVENTS['notification'], message)

    def __un_subscribe_at_pubnub(self):
        if self.__pubnub and self.is_subscribed():
            self.__pubnub.unsubscribe(self.__subscription['deliveryMode']['address'])

    def __get_full_events_filter(self):
        return [self.__platform.api_url(e) for e in self.__event_filters]

    def __set_timeout(self):
        time_to_expiration = self.__subscription['expiresIn'] - RENEW_HANDICAP
        self.__timeout = Timer(time_to_expiration, self.renew)
        self.__timeout.start()

    def __clear_timeout(self):
        if self.__timeout:
            self.__timeout.cancel()

    def _get_pubnub(self):
        return self.__pubnub


if __name__ == '__main__':
    pass