import urllib
import base64
import sys
import re


def is_third():
    return sys.version_info >= (3, 0)


def urlencode(s):
    if hasattr(urllib, 'urlencode'):
        return urllib.urlencode(s)
    elif hasattr(urllib, 'parse'):
        return urllib.parse.urlencode(s)
    else:
        raise Exception("No urlencode")


def iterator(thing):
    return thing.iteritems() if hasattr(thing, 'iteritems') else iter(thing.items())


def base64encode(s):
    if is_third():
        return str(base64.b64encode(bytes(s, 'utf8')), 'utf8')
    else:
        return base64.b64encode(s)


def tostr(s):
    if is_third():
        return str(s, 'utf8')
    else:
        return str(s)


def clean_decrypted(s):
    if is_third():
        return re.sub(r"[\u0001-\u0010]", '', s).strip()
    else:
        return s.replace('\x05', '')