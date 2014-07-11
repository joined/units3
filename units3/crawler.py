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

    def __init__(self, resources=None, auth_key=None):
        self.resources = resources
        self.auth_key = auth_key
        self.cookie = None
        # Connection pool to reuse connections
        self.http = urllib3.connection_from_url('https://esse3.units.it')

        # If auth key was given but it is not valid, raise exception
        if auth_key is not None and not self.auth_is_valid():
            raise AuthError()

    def renew_cookie(self, first_try=True):
        """
        Renews cookie for the current user,
        and checks if auth info is ok.
        """

        headers = {
            'User-Agent': 'Python/3.4',
            'Authorization': 'Basic ' + self.auth_key
        }

        # Set cookie if present
        if self.cookie is not None:
            headers['Cookie'] = self.cookie

        # URL to use to retrieve cookie and check auth
        test_url = '/auth/studente/Libretto/LibrettoHome.do'
        req = self.http.request('GET', test_url, headers=headers)

        if req.status == 401:
            # If it's not the first time I get 401, the
            # auth data is wrong
            if not first_try:
                raise AuthError()

            else:
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

    def resource_fetch(self, resource):
        """
        Fetches a single resource using auth if needed,
        and returns a tuple containind resource name and retrieved data
        """
        headers = {'User-Agent': 'Python/3.4'}

        # Add auth if needed
        if self.auth_key is not None:
            headers['Cookie'] = self.cookie
            headers['Authorization'] = 'Basic ' + self.auth_key

        # Unpack resource
        res_name, res_url = resource
        req = self.http.request('GET', res_url, headers=headers)

        return (res_name, req.data)

    def get_results(self):
        # If we are fetching protected resources, need to renew cookie
        if self.auth_key is not None:
            self.renew_cookie()

        # Threads Powah!
        pool = ThreadPoolExecutor(max_workers=2)

        results = {}
        # Dict containing results to be parsed
        to_parse = {}

        for (res_name, res_url) in self.resources.items():
            # If parser doesn't exist, say it
            if not hasattr(Parser, res_name):
                results[res_name] = "Parser non implementato."
            else:
                to_parse[res_name] = res_url

        # Parallel mapping
        responses = pool.map(self.resource_fetch, to_parse.items())

        for response in responses:
            res_name, res_data = response

            parsed_response = getattr(Parser(res_data), res_name)()

            results[res_name] = parsed_response

        pool.shutdown()

        return results
