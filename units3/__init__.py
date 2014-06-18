#!.env/bin/python
# -*- coding: UTF-8 -*- #
import urllib2
import base64
import re
from flask import Flask, jsonify, request, make_response
from bs4 import BeautifulSoup

app = Flask(__name__)

cookie = None

# Base URL of Univ. of Trieste ESSE3 service
baseurl = 'https://esse3.units.it/auth/studente/'

# Single ESSE3 services URLs
services_urls = {'libretto': baseurl + 'Libretto/LibrettoHome.do',
                 'tasse': baseurl + 'Tasse/ListaFatture.do',
                 'pren_appelli': baseurl + 'Appelli/AppelliF.do',
                 'pren_effettuate': baseurl + 'Appelli/BachecaPrenotazioni.do',
                 'prove_parziali': baseurl + 'Appelli/AppelliP.do'}

# Errors text
errors_text = {'dati_non_validi': 'Dati di accesso non validi'}


# Exception raised if auth is not valid
class AuthError(Exception):
    pass


# Gets page with HTTP basic auth setting cookies
def get_page_with_auth(url, auth_key, first_try=True):
    global cookie

    u2_req = urllib2.Request(url)

    # Header for HTTP basic auth
    u2_req.add_header('Authorization', 'Basic ' + auth_key)

    # Add cookie with JSESSIONID, if present
    if cookie is not None:
        u2_req.add_header('Cookie', cookie)

    try:
        response = urllib2.urlopen(u2_req)
    # If I get an HTTP error doing the request
    except urllib2.HTTPError as e:
        if e.code == 401:
            # If it's not the first time I get 401, the
            # auth data is wrong
            if not first_try:
                raise AuthError()

            else:
                # If it's the first time I try, I have to load
                # the cookies
                cookie = e.info().getheader('Set-Cookie')

                # Repeat function, reporting it's not the first try
                return get_page_with_auth(url, auth_key, False)
    else:
        return response.read()


# Parsing of "libretto" page
def parse_libretto(html_libretto):
    soup_libretto = BeautifulSoup(html_libretto)

    # List of of table rows I need
    lista_righe = soup_libretto.find(
        'table', {'class': 'detail_table'}).find_all('tr')

    a = []

    # Skip the first line, garbage
    for riga in lista_righe[1:]:
        # Verify if "voto - data" is present, they could be not
        if riga.contents[10].string is not None:
            voto_e_data = riga.contents[10].string.split(u'\u00a0-\u00a0')
            voto = voto_e_data[0]
            data = voto_e_data[1]
        else:
            voto = None
            data = None

        esame = {'anno_di_corso': riga.contents[1].string,
                 'nome': riga.contents[2].string.split(' - ')[1],
                 'codice': riga.contents[2].string.split(' - ')[0],
                 'crediti': riga.contents[7].string,
                 'anno_frequenza': riga.contents[9].string,
                 'voto': voto,
                 'data': data}

        a.append(esame)

    return a


# Parsing of "tasse" page
def parse_tasse(html_tasse):
    soup_tasse = BeautifulSoup(html_tasse)

    # List of of table rows I need
    lista_righe = soup_tasse.find(
        'table', {'class': 'detail_table'}).find_all('tr')

    a = []

    # Skip the first line, garbage
    for riga in lista_righe[1:]:
        if len(riga.contents) > 3:
            # Convert to float the value
            importo = float(riga.contents[6].string[2:].replace(',', '.'))

            # If there's the green semaphore the fee is payed
            if ('semaf_v' in str(riga.contents[7])):
                stato = 'pagato'
            # Otherwise not
            else:
                stato = 'da_pagare'

            tassa = {'codice_fattura': riga.contents[1].string,
                     'codice_bollettino': riga.contents[2].string,
                     'anno': riga.contents[3].string,
                     'descrizione': riga.contents[4].string,
                     'data_scadenza': riga.contents[5].string,
                     'importo': importo,
                     'stato': stato
                     }

            a.append(tassa)

    return a


# Check if auth_key is present and in a valid format
def auth_is_valid(auth_key):
    if auth_key is None:
        return False
    else:
        # Check it's in the right format
        regex = r'[a-z0-9]{1,}:[A-Z0-9]{1,}'
        try:
            decoded_key = base64.b64decode(auth_key)
        # If a TypeError is raised, the key is a mess
        except TypeError:
            return False

        return True if re.search(regex, decoded_key) else False


# When used as decorator after route declaration,
# it checks for auth key
def require_auth(func):
    func._require_auth = True
    return func


# Does the auth check on every route with require_auth decorator
@app.before_request
def before_request(*args, **kwargs):
    print('## RICHIESTA RICEVUTA ##')

    # By default, auth is not required
    auth_required = False

    # Check if auth is required in this route
    if request.endpoint in app.view_functions:
        view_func = app.view_functions[request.endpoint]
        auth_required = hasattr(view_func, '_require_auth')

    if auth_required and not auth_is_valid(request.args.get('auth_key')):
        return jsonify({'errore': errors_text['dati_non_validi']})


# Return a JSON with error on 404, insted of ugly HTML
@app.errorhandler(404)
def not_found(errore):
    return make_response(jsonify({'errore': 'Risorsa non trovata'}), 404)


# Route for "libretto" resource
@app.route('/libretto', methods=['GET'])
@require_auth
def get_libretto():
    try:
        html_libretto = get_page_with_auth(services_urls['libretto'],
                                           request.args.get('auth_key'))
    except AuthError:
        return jsonify({'errore': errors_text['dati_non_validi']})
    else:
        return jsonify({'libretto': parse_libretto(html_libretto)})


# Route for "tasse" resource
@app.route('/tasse', methods=['GET'])
@require_auth
def get_tasse():
    try:
        html_tasse = get_page_with_auth(services_urls['tasse'],
                                        request.args.get('auth_key'))
    except AuthError:
        return jsonify({'errore': errors_text['dati_non_validi']})
    else:
        return jsonify({'tasse': parse_tasse(html_tasse)})

if __name__ == '__main__':
    app.run(debug=True)
