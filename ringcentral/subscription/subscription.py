#!/usr/bin/env python
# encoding: utf-8
import json
import base64
from threading import Timer
from ..core.observable import Observable
from .events import Events

RENEW_HANDICAP = 60


class Subscription(Observable):
    def __init__(self, platform, pubnub_factory):
        Observable.__init__(self)
        self._pubnub_factory = pubnub_factory
        self._platform = platform
        self._event_filters = []
        self._timeout = None
        self._subscription = {
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
        self._pubnub = None

    def pubnub(self):
        return self._pubnub

    def register(self, events=None):
        if self.alive():
            return self.renew(events=events)
        else:
            return self.subscribe(events=events)

    def add_events(self, events):
        self._event_filters += events
        pass

    def set_events(self, events):
        self._event_filters = events

    def subscribe(self, events=None):

        if events:
            self.set_events(events)

        if not self._event_filters or len(self._event_filters) == 0:
            raise Exception('Events are undefined')

        try:
            response = self._platform.post('/restapi/v1.0/subscription', body={
                'eventFilters': self._get_full_events_filter(),
                'deliveryMode': {
                    'transportType': 'PubNub'
                }
            })

            self.set_subscription(response.json_dict())
            self._subscribe_at_pubnub()
            self.emit(Events.subscribeSuccess, response)

            return response

        except Exception as e:
            self.reset()
            self.emit(Events.subscribeError, e)
            raise

    def renew(self, events=None):

        if events:
            self.set_events(events)

        if not self.alive():
            raise Exception('Subscription is not alive')

        if not self._event_filters or len(self._event_filters) == 0:
            raise Exception('Events are undefined')

        self._clear_timeout()

        try:
            response = self._platform.put('/restapi/v1.0/subscription' + self._subscription['id'], body={
                'eventFilters': self._get_full_events_filter()
            })

            self.set_subscription(response.json_dict())
            self.emit(Events.renewSuccess, response)

            return response

        except Exception as e:
            self.reset()
            self.emit(Events.renewError, e)
            raise

    def remove(self):
        if not self.alive():
            raise Exception('Subscription is not alive')

        try:
            response = self._platform.delete('/restapi/v1.0/subscription' + self._subscription['id'])

            self.reset()
            self.emit(Events.removeSuccess, response)

            return response

        except Exception as e:
            self.reset()
            self.emit(Events.removeError, e)

    def alive(self):
        s = self._subscription
        return ('deliveryMode' in s and s['deliveryMode']) and \
               ('subscriberKey' in s['deliveryMode'] and s['deliveryMode']['subscriberKey']) and \
               ('address' in s['deliveryMode'] and s['deliveryMode']['address'])

    def subscription(self):
        return self._subscription

    def set_subscription(self, data):
        self._clear_timeout()
        self._subscription = data
        self._set_timeout()

    def reset(self):
        self._clear_timeout()
        self._unsubscribe_at_pubnub()
        self._subscription = None

    def destroy(self):
        self.reset()
        self.off()

    def _subscribe_at_pubnub(self):
        if not self.alive():
            raise Exception('Subscription is not alive')

        s_key = self._subscription['deliveryMode']['subscriberKey']
        self._pubnub = self._pubnub_factory.pubnub(subscribe_key=s_key, ssl_on=False, publish_key='')

        def callback(message, channel=''):
            self._notify(message)

        def error(message):
            print("ERROR : " + str(message))  # FIXME Handle this

        def connect(message):
            print("CONNECTED")

        def reconnect(message):
            print("RECONNECTED")

        def disconnect(message):
            print("DISCONNECTED")

        self._pubnub.subscribe(self._subscription['deliveryMode']['address'], callback=callback, error=error,
                               connect=connect, reconnect=reconnect, disconnect=disconnect)

    def _notify(self, message):
        message = self._decrypt(message)
        self.emit(Events.notification, message)

    def _decrypt(self, message):
        if not self.alive():
            raise Exception('Subscription is not alive')

        from pubnub import AES

        delivery_mode = self._subscription['deliveryMode']
        is_encrypted = ('encryption' in delivery_mode) and ('encryptionKey' in delivery_mode)

        if is_encrypted:
            key = base64.b64decode(self._subscription['deliveryMode']['encryptionKey'])
            data = base64.b64decode(message)
            obj2 = AES.new(key)
            decrypted = str(obj2.decrypt(data)).replace('\x05', '')
            message = json.loads(decrypted)

        return message

    def _unsubscribe_at_pubnub(self):
        if self._pubnub and self.alive():
            self._pubnub.unsubscribe(self._subscription['deliveryMode']['address'])

    def _get_full_events_filter(self):
        return [self._platform.create_url(e) for e in self._event_filters]

    def _set_timeout(self):
        time_to_expiration = self._subscription['expiresIn'] - RENEW_HANDICAP
        self._timeout = Timer(time_to_expiration, self.renew)
        self._timeout.start()

    def _clear_timeout(self):
        if self._timeout:
            self._timeout.cancel()


if __name__ == '__main__':
    pass
