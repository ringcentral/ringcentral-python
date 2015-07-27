#!/usr/bin/env python
# encoding: utf-8

import unittest
from .. import *
from ..http.mocks.authentication_mock import AuthenticationMock


class TestCase(unittest.TestCase):
    def __init__(self, method_name=None):
        unittest.TestCase.__init__(self, method_name)

    def get_sdk(self, authorized=True):
        sdk = RCSDK('whatever', 'whatever', 'https://whatever')

        context = sdk.get_context()

        context.use_pubnub_stub(True).use_request_stub(True)

        if authorized:
            context.get_mocks().add(AuthenticationMock())
            sdk.get_platform().authorize('18881112233', None, 'password', True)

        return sdk


class Spy(object):
    def __init__(self):
        self.args = None

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
