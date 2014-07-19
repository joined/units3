# -*- coding: utf-8 -*-
from base64 import b64encode

"""
Common project utilities
"""


def encode_auth(auth):
    """
    Takes auth dictionary and calculates HTTP-compatible
    base64-encoded key
    """
    username = auth['username'].encode('utf-8')
    password = auth['password'].encode('utf-8')

    return b64encode(username + b':' + password).decode('utf-8')
