# -*- coding: utf-8 -*-
from units3.crawler import Crawler
from units3.exceptions import AuthError
from flask import Flask, jsonify, request, make_response

__author__ = "Lorenzo Gasparini"
__license__ = "GPLv3"
__version__ = "0.1dev"
__email__ = "joined@me.com"

app = Flask(__name__)

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

# Resources that don't need it
open_resources = {'home': '/Home.do'}


# On 404 error
@app.errorhandler(404)
def not_found():
    """Return a JSON with error on 404, insted of ugly HTML"""
    return make_response(
        jsonify({'errore': 'Una o più risorse non trovate.'}),
        404)


def bad_auth():
    """Response for bad authentication info"""
    return make_response(
        jsonify({'errore': 'Autenticazione non valida.'}),
        401)


@app.route('/protected/', methods=['GET'])
def get_protected():
    """
    Route to get multiple protected resources at once.
    The querystring should be:
    http://localhost/protected/?resources=fist,second,third&auth_key=mykey
    """

    # Get resources requested via GET method
    req_resources = request.args.get('resources')
    if ',' in req_resources:
        req_resources = req_resources.split(',')

    # If at least one of the resources requested doesn't exist, 404!
    if not set(protected_resources.keys()) >= set(req_resources):
        return not_found()

    # Get auth_key sent via GET method
    auth_key = request.args.get('auth_key')

    # Check if auth_key was given, otherwise 401!
    if auth_key is None:
        return bad_auth()

    # Crawler-friendly dictionary of services to be retrieved
    resources = {res_name: res_url
                 for (res_name, res_url)
                 in protected_resources.items()
                 if res_name in req_resources}
    try:
        crawler = Crawler(resources=resources, auth_key=auth_key)
    except AuthError:
        # On wrong auth info, 401!
        return bad_auth()
    else:
        return jsonify(crawler.get_results())


@app.route('/open/', methods=['GET'])
def get_open():
    """
    Route to get multiple open resources at once.
    The querystring should be:
    http://localhost/open/?resources=fist,second,third
    """

    # Get resources requested via GET method
    req_resources = request.args.get('resources')
    if ',' in req_resources:
        req_resources = req_resources.split(',')

    # If at least one of the resources requested doesn't exist, 404!
    if not set(open_resources.keys()) >= set(req_resources):
        return not_found()

    # Crawler-friendly dictionary of services to be retrieved
    resources = {res_name: res_url
                 for (res_name, res_url)
                 in open_resources.items()
                 if res_name in req_resources}

    crawler = Crawler(resources=resources)

    return jsonify(crawler.get_results())


@app.route('/protected/<resource>', methods=['GET'])
def get_single_protected(resource):
    """
    Route to get a single protected resource.
    The querystring should be:
    http://localhost/protected/resource_name
    """

    # Get auth_key sent via GET method
    auth_key = request.args.get('auth_key')

    # On empty auth info, 401!
    if auth_key is None:
        return bad_auth()

    # Check if resource exists, otherwise 404!
    if resource not in protected_resources.keys():
        return not_found()

    # Crawler-friendly dictionary with resource
    friendly_resource = {resource: protected_resources[resource]}

    try:
        crawler = Crawler(resources=friendly_resource, auth_key=auth_key)
    except AuthError:
        # On wrong auth info, 401!
        return bad_auth()
    else:
        return jsonify(crawler.get_results())


@app.route('/open/<resource>', methods=['GET'])
def get_single_open(resource):
    """
    Route to get a single open resource.
    The querystring should be:
    http://localhost/open/resource_name
    """

    # Check if resource exists, otherwise 404!
    if resource not in open_resources.keys():
        return not_found()

    # Crawler-friendly dictionary with resource
    friendly_resource = {resource: open_resources[resource]}

    crawler = Crawler(resources=friendly_resource)

    return jsonify(crawler.get_results())
