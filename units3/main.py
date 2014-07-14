# -*- coding: utf-8 -*-
from base64 import b64encode
from units3.crawler import Crawler
from units3.exceptions import AuthError
from urllib3.exceptions import MaxRetryError
from flask import Flask, request, Response, jsonify, make_response
from functools import wraps

# Resources that need authentication
protected_resources = {
    'iscrizioni': '/auth/studente/ListaIscrizioni.do',
    'libretto': '/auth/studente/Libretto/LibrettoHome.do',
    'pagamenti': '/auth/studente/Tasse/ListaFatture.do',
    'certificazioni': '/auth/studente/Certificati/ListaCertificati.do',
    'prenotazione_appelli': '/auth/studente/Appelli/AppelliF.do',
    'prenotazioni_effettuate': '/auth/studente/Appelli/BachecaPrenotazioni.do',
    'prove_parziali': '/auth/studente/Appelli/AppelliP.do'
}


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


@app.route('/protected/', methods=['GET'])
@requires_auth
def get_protected():
    """
    Route to get multiple protected resources at once.
    The querystring should be:
    http://localhost/protected/?select=fist,second,third
    """

    req_resources = request.args.get('select')

    # Check if 'select' parameter was set, if not 404
    if not req_resources:
        return not_found()

    # Split requested resources if there are more than one
    if ',' in req_resources:
        req_resources = req_resources.split(',')

    # If at least one of the resources requested doesn't exist, 404!
    if not set(protected_resources.keys()) >= set(req_resources):
        return not_found()

    # Get auth from request and encode it to a Crawler-friendly format
    auth = request.authorization
    encoded_auth = b64encode(auth.username + u':' + auth.password)

    # Crawler-friendly dictionary of services to be retrieved
    resources = {res_name: res_url
                 for (res_name, res_url)
                 in protected_resources.items()
                 if res_name in req_resources}

    try:
        crawler = Crawler(resources, encoded_auth)

        results = crawler.get_results()
    except AuthError:
        # On wrong auth info, 401!
        return authenticate()
    except MaxRetryError:
        # Internal connection problems
        return connection_error()
    else:
        return jsonify(results)


@app.route('/protected/<resource>', methods=['GET'])
@requires_auth
def get_single_protected(resource):
    """
    Route to get a single protected resource.
    The querystring should be:
    http://localhost/protected/resource_name
    """

    auth = request.authorization.values()
    encoded_auth = b64encode(':'.join(auth.values()).encode('utf-8'))

    # Check if resource exists, otherwise 404!
    if resource not in protected_resources.keys():
        return not_found()

    # Crawler-friendly dictionary with resource
    friendly_resource = {resource: protected_resources[resource]}

    try:
        crawler = Crawler(resources=friendly_resource, auth_key=encoded_auth)

        results = crawler.get_results()
    except AuthError:
        # On wrong auth info, 401!
        return authenticate()
    except MaxRetryError:
        # Internal connection problems
        return connection_error()
    else:
        return jsonify(results)
