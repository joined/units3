# -*- coding: utf-8 -*-
from flask import Response, make_response, jsonify

"""
Mix of useful Classes / functions which
don't have another place
"""


class JSONResponse(Response):

    """Subclasses Response to set default mimetype to json"""
    default_mimetype = 'application/json'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return make_response(
        jsonify({'errore': 'Credenziali errate'}),
        401,
        {'WWW-Authenticate': 'Basic realm="units3"'}
    )


def connection_error():
    """Response for internal connection problem"""
    return make_response(
        jsonify({'errore': 'Problema di connessione con ESSE3'}),
        500
    )
