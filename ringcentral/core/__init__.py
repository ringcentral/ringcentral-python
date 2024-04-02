import urllib
import base64
import sys
import re


def is_third():
    return sys.version_info >= (3, 0)


def urlencode(s):
    """
        Encodes the given dictionary `s` into a URL-encoded string.

        Parameters:
            s (dict): A dictionary containing the key-value pairs to be encoded.

        Returns:
            str: A URL-encoded string representing the input dictionary.

        Raises:
            Exception: If neither `urllib.urlencode` nor `urllib.parse.urlencode` is available.

        Note:
            This function checks for the presence of `urllib.urlencode` and `urllib.parse.urlencode`
            to ensure compatibility across Python 2 and Python 3.
    """
    if hasattr(urllib, 'urlencode'):
        return urllib.urlencode(s)
    elif hasattr(urllib, 'parse'):
        return urllib.parse.urlencode(s)
    else:
        raise Exception("No urlencode")


def iterator(thing):
    """
    Returns an iterator over key-value pairs of `thing`.

    If `thing` has an `iteritems` method, it is used; otherwise, `thing.items()` is iterated over.

    Parameters:
        thing: An iterable object.

    Returns:
        iterator: An iterator over the key-value pairs of `thing`.
    """
    return thing.iteritems() if hasattr(thing, 'iteritems') else iter(thing.items())


def base64encode(s):
    """
    Encodes the input string `s` into base64 format.

    Parameters:
        s (str): The string to be encoded.

    Returns:
        str: The base64 encoded string.

    """
    # Use Python 3 compatible base64 encoding if detected, otherwise use default encoding
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
    """
    Cleans the decrypted string `s` by removing specific control characters.

    Parameters:
        s (str): The decrypted string to be cleaned.

    Returns:
        str: The cleaned decrypted string.
    """
    if is_third():
        return re.sub(r"[\u0001-\u0010]", '', s).strip()
    else:
        return s.replace('\x05', '')