from units3.crawler import Crawler
from units3.exceptions import AuthError
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

protected_resources = {
    'iscrizioni': '/auth/studente/ListaIscrizioni.do',
    'libretto': '/auth/studente/Libretto/LibrettoHome.do',
    'pagamenti': '/auth/studente/Tasse/ListaFatture.do',
    'certificazioni': '/auth/studente/Certificati/ListaCertificati.do',
    'prenotazione_appelli': '/auth/studente/Appelli/AppelliF.do',
    'prenotazioni_effettuate': '/auth/studente/Appelli/BachecaPrenotazioni.do',
    'prove_parziali': '/auth/studente/Appelli/AppelliP.do'
}

open_resources = {'home': '/Home.do'}


# Return a JSON with error on 404, insted of ugly HTML
@app.errorhandler(404)
def not_found(errore):
    return make_response(jsonify({'errore': 'Risorsa non trovata'}), 404)


# Route for protected resources
@app.route('/protected/', methods=['GET'])
def get_protected():
    # TODO: CONTROLLO SE ESISTONO LE RISORSE
    req_resources = request.args.get('resources')

    if req_resources is None:
        return jsonify({'errore': 'Richiesta errata.'})

    auth_key = request.args.get('auth_key')

    if auth_key is None:
        return jsonify({'errore': 'Dati di accesso non pervenuti.'})

    resources = {res_name: res_url
                 for (res_name, res_url)
                 in protected_resources.items()
                 if res_name in req_resources.split(',')}
    try:
        crawler = Crawler(resources=resources, auth_key=auth_key)
    except AuthError:
        return jsonify({'errore': 'Dati di accesso non validi.'})
    else:
        return jsonify(crawler.get_results())


# Route for single protected resource
@app.route('/protected/<resource>', methods=['GET'])
def get_single_protected(resource):
    auth_key = request.args.get('auth_key')

    if auth_key is None:
        return jsonify({'errore': 'Dati di accesso non pervenuti.'})

    if resource not in protected_resources.keys():
        return jsonify({'errore': 'Risorsa non trovata.'})

    res_url = protected_resources[resource]
    try:
        crawler = Crawler(resources={resource: res_url}, auth_key=auth_key)
    except AuthError:
        return jsonify({'errore': 'Dati di accesso non validi.'})
    else:
        return jsonify(crawler.get_results())


# Route for single open resource
@app.route('/open/<resource>', methods=['GET'])
def get_single_open(resource):
    if resource not in open_resources.keys():
        return jsonify({'errore': 'Risorsa non trovata.'})

    res_url = open_resources[resource]

    crawler = Crawler(resources={resource: res_url})

    return jsonify(crawler.get_results())

if __name__ == '__main__':
    app.run(debug=True)
