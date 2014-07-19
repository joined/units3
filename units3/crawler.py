# -*- coding: utf-8 -*-
import urllib3
import base64
import re
from units3.exceptions import AuthError
from units3.parser import Parser
from concurrent.futures import ThreadPoolExecutor


class Crawler:

    """
    Crawler for units ESSE3 service.
    Given resources and auth_key, it crawls
    the website and returns the wanted results
    after having parsed them.
    """

    # ESSE3 resources that are available
    available_resources = {
        'home': '/Home.do',
        # 'iscrizioni': '/auth/studente/ListaIscrizioni.do',
        'pagamenti': '/auth/studente/Tasse/ListaFatture.do',
        # 'certificazioni': '/auth/studente/Certificati/ListaCertificati.do',
        'libretto': '/auth/studente/Libretto/LibrettoHome.do',
        'prenotazione_appelli': '/auth/studente/Appelli/AppelliF.do',
        'prenotazioni_effettuate': '/auth/studente/Appelli/'
                                   'BachecaPrenotazioni.do'
        # 'prove_parziali': '/auth/studente/Appelli/AppelliP.do',
    }

    def __init__(self, resources, auth_key):
        # Disable SSL warning.
        urllib3.disable_warnings()

        self.resources = resources
        self.auth_key = auth_key
        self.cookie = ''

        # Connection pool to reuse connections
        self.http = urllib3.connection_from_url('https://esse3.units.it')

        # If auth key is not in a valid format, raise exception
        if not self.auth_is_valid():
            raise AuthError()

    def renew_cookie(self, first_try=True):
        """
        Renews cookie for the current user,
        checking if auth info is ok.
        """
        headers = {
            'User-Agent': 'Python/3.4',
            'Authorization': 'Basic ' + self.auth_key,
            'Cookie': self.cookie
        }

        # URL to use to retrieve cookie / check auth
        test_url = '/auth/studente/Libretto/LibrettoHome.do'
        # Make a HEAD request to retrieve cookie / check auth
        req = self.http.request('HEAD', test_url, headers=headers)

        if req.status == 401:
            # If it's not the first time I get 401, the
            # auth data is wrong
            if not first_try:
                raise AuthError()

            else:
                # Extract new cookie from response headers
                self.cookie = req.headers['set-cookie']

                # Repeat function, reporting it's not the first try
                self.renew_cookie(first_try=False)

    def auth_is_valid(self):
        """Checks if auth_key is in the right format"""
        try:
            decoded_key = base64.b64decode(self.auth_key)
        # If a TypeError is raised, the key is a mess
        except Exception:
            return False

        # RegEx Powah!
        regex = r'[a-z0-9]{1,}:[A-Z0-9]{1,}'
        return True if re.search(regex, str(decoded_key)) else False

    def resource_fetch(self, res_name):
        """
        Fetches a single resource using auth if needed,
        and returns a tuple containing resource name and retrieved data
        """
        headers = {
            'User-Agent': 'Python/3.4',
            'Cookie': self.cookie,
            'Authorization': 'Basic ' + self.auth_key
        }

        # Get resource URL from list of available resources
        res_url = self.available_resources[res_name]
        req = self.http.request('GET', res_url, headers=headers)

        return (res_name, req.data)

    def get_results(self):
        """
        Maps the resources to be downloaded, parses them
        and returns a dictionary containing the results
        """
        # Renew cookie
        self.renew_cookie()

        # Threads Powah!
        pool = ThreadPoolExecutor(max_workers=2)

        results = {
            res_name: getattr(Parser(res_data), res_name)()
            for (res_name, res_data)
            in pool.map(self.resource_fetch, self.resources)
        }

        pool.shutdown()

        return results
