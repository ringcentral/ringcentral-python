#!/usr/bin/env python
# encoding: utf-8

from ..core import Observable


class PubnubMock(Observable):
    def __init__(self):
        Observable.__init__(self)

    def subscribe(self, channel, callback=None, error=None, connect=None, reconnect=None, disconnect=None):
        self.on('message', callback)

    def unsubscribe(self, channel):
        pass

    def receive_message(self, message):
        self.emit('message', message)