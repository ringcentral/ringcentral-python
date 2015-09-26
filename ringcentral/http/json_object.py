# !/usr/bin/env python
# encoding: utf-8

PYTHON_KEYWORDS = (
    "and", "del", "from", "not", "while", "as", "elif", "global", "or", "with", "assert", "else", "if", "pass", "yield",
    "break", "except", "import", "rint", "class", "exec", "in", "raise", "continue", "finally", "is", "return", "def",
    "for", "lambda", "try",)


class JsonObject:
    def __init__(self):
        pass


def safe_name(n):
    if n in PYTHON_KEYWORDS:
        return n + "_"
    else:
        return n


def unfold(d):
    if isinstance(d, dict):
        o = JsonObject()
        for k, v in d.iteritems():
            o.__dict__[safe_name(k)] = unfold(v)
        return o
    elif isinstance(d, list):
        o = [unfold(x) for x in d]
        return o
    else:
        return d
