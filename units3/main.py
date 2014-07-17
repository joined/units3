# -*- coding: utf-8 -*-
from base64 import b64encode
from units3.crawler import Crawler
from units3.exceptions import AuthError
from urllib3.exceptions import MaxRetryError
from flask import Flask, request, Response, jsonify, make_response
from functools import wraps


class JSONResponse(Response):
    """Subclasses Response to set default mimetype to json"""
    default_mimetype = 'application/json'


app = Flask(__name__)
app.response_class = JSONResponse


@app.errorhandler(404)
def not_found(e=None):
    """Return a JSON with error on 404, insted of ugly HTML"""
    return make_response(
        jsonify({'errore': u'Una o più risorse non trovate.'}),
        404
    )


def requires_auth(f):
    """Decorator for authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if (not auth) or (not auth.username) or (not auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


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


def encode_auth(auth):
    username = auth['username'].encode('utf-8')
    password = auth['password'].encode('utf-8')

    return b64encode(username + b':' + password).decode('utf-8')


@app.route('/', methods=['GET'])
@requires_auth
def get_resources():
    """
    Route to get multiple resources at once.
    The querystring should be:
    http://localhost/?select=fist,second,third
    """

    req_resources = request.args.get('select')

    # Check if 'select' parameter was set, if not 404
    if not req_resources:
        return not_found()

    # Split requested resources if there are more than one
    if ',' in req_resources:
        req_resources = req_resources.split(',')

    # If at least one of the resources requested doesn't exist, 404!
    if not set(Crawler.available_resources.keys()) >= set(req_resources):
        return not_found()

    encoded_auth = encode_auth(request.authorization)

    try:
        crawler = Crawler(req_resources, encoded_auth)

        results = crawler.get_results()
    except AuthError:
        # On wrong auth info, 401!
        return authenticate()
    except MaxRetryError:
        # Internal connection problems
        return connection_error()
    else:
        return jsonify(results)


@app.route('/<resource>', methods=['GET'])
@requires_auth
def get_single_resource(resource):
    """
    Route to get a single resource.
    The querystring should be:
    http://localhost/resource_name
    """

    encoded_auth = encode_auth(request.authorization)

    # Check if resource exists, otherwise 404!
    if resource not in Crawler.available_resources.keys():
        return not_found()

    try:
        crawler = Crawler(resources=resource, auth_key=encoded_auth)

        results = crawler.get_results()
    except AuthError:
        # On wrong auth info, 401!
        return authenticate()
    except MaxRetryError:
        # Internal connection problems
        return connection_error()
    else:
        return jsonify(results)
