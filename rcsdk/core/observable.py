#!/usr/bin/env python
# encoding: utf-8


class Observable:
    def __init__(self):
        self.__listeners = {}

    def on(self, event, fn):
        if event not in self.__listeners:
            self.__listeners[event] = []
        self.__listeners[event].append(fn)

    def emit(self, event, data=None):
        res = None

        # TODO Replace with reduce
        if event in self.__listeners:
            for l in self.__listeners[event]:
                res = l(data)
                if not res:  # TODO Strict type check
                    break

        return res

    def off(self, event='', fn=None):
        if event:
            if fn:
                for l in self.__listeners[event]:
                    if l == fn:
                        pass  # TODO
            else:
                self.__listeners[event] = []
        else:
            self.__listeners = {}

        return self
