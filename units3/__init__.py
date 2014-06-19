#!.env/bin/python
# -*- coding: UTF-8 -*- #
import urllib2
import base64
import re
import sqlite3
from flask import Flask, jsonify, request, make_response, g
from bs4 import BeautifulSoup

app = Flask(__name__)

DATABASE = 'db/database.db'
# cookie = None

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


# Gets the SQLite db
def connect_db():
    return sqlite3.connect(DATABASE)


# Gets a user's cookie from db
def get_user_cookie(user):
    print("*get_user_cookie*")
    db = g.db
    cur = db.cursor()
    res = cur.execute('SELECT cookie FROM cookies WHERE user=?', (user,))
    cookie = res.fetchone()
    return cookie[0] if cookie is not None else None


# Updates the cookie for a user if already there,
# otherwise inserts user+cookie in database
def set_user_cookie(user, cookie):
    print("*set_user_cookie* con cookie:" + cookie)
    db = g.db
    cur = db.cursor()
    cur.execute('INSERT OR IGNORE INTO cookies VALUES (?,?)', (user, cookie))
    cur.execute('UPDATE cookies SET cookie=? WHERE user=?', (cookie, user))
    db.commit()


# Gets page with HTTP basic auth setting cookies
def get_page_with_auth(url, auth_key, first_try=True):
    user = base64.b64decode(auth_key).split(':')[0]

    u2_req = urllib2.Request(url)

    # Header for HTTP basic auth
    u2_req.add_header('Authorization', 'Basic ' + auth_key)

    # Gets the user cookie from database
    db_cookie = get_user_cookie(user)

    # Add cookie with JSESSIONID, if present
    if db_cookie is not None:
        u2_req.add_header('Cookie', db_cookie)

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
                # If it's the first time I try, I have to load the
                # cookies in the database
                cookie_to_set = e.info().getheader('Set-Cookie')

                # It can be empty if auth data is wrong
                if cookie_to_set is not None:
                    set_user_cookie(user, cookie_to_set)

                # Repeat function, reporting it's not the first try
                return get_page_with_auth(url, auth_key, False)
    else:
        return response.read()


# Parsing of "libretto" page
def parse_libretto(html_libretto):
    soup_libretto = BeautifulSoup(html_libretto)

    # List of of table rows I need
    rows_list = soup_libretto.find(
        'table', {'class': 'detail_table'}).find_all('tr')

    a = []

    # Skip the first line, garbage
    for row in rows_list[1:]:
        # Verify if "voto - data" is present, they could be not
        if row.contents[10].string is None:
            voto, data = None, None
        else:
            voto, data = row.contents[10].string.split(u'\u00a0-\u00a0')

        esame = {'anno_di_corso': row.contents[1].string,
                 'nome': row.contents[2].string.split(' - ')[1],
                 'codice': row.contents[2].string.split(' - ')[0],
                 'crediti': row.contents[7].string,
                 'anno_frequenza': row.contents[9].string,
                 'voto': voto,
                 'data': data}

        a.append(esame)

    return a


# Parsing of "tasse" page
def parse_tasse(html_tasse):
    soup_tasse = BeautifulSoup(html_tasse)

    # List of of table rows I need
    rows_list = soup_tasse.find(
        'table', {'class': 'detail_table'}).find_all('tr')

    a = []

    # Skip the first line, garbage
    for row in rows_list[1:]:
        if len(row.contents) > 3:
            # Convert to float the value
            importo = float(row.contents[6].string[2:].replace(',', '.'))

            # If there's the green semaphore the fee is payed
            if ('semaf_v' in str(row.contents[7])):
                stato = 'pagato'
            # Otherwise not
            else:
                stato = 'da_pagare'

            tassa = {'codice_fattura': row.contents[1].string,
                     'codice_bollettino': row.contents[2].string,
                     'anno': row.contents[3].string,
                     'descrizione': row.contents[4].string,
                     'data_scadenza': row.contents[5].string,
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
    print('*richiesta ricevuta')

    g.db = connect_db()

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


# Closes connection on app closing
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


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
