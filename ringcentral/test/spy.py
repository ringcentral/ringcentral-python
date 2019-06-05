#!/usr/bin/env python
# encoding: utf-8

class Spy(object):
    def __init__(self):
        self.args = None

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
