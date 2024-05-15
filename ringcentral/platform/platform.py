import sys
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from observable import Observable
from functools import reduce
from .auth import Auth
from .events import Events
from ..core import base64encode
import warnings

ACCOUNT_ID = '~'
ACCOUNT_PREFIX = '/account/'
URL_PREFIX = '/restapi'
TOKEN_ENDPOINT = '/restapi/oauth/token'
REVOKE_ENDPOINT = '/restapi/oauth/revoke'
AUTHORIZE_ENDPOINT = '/restapi/oauth/authorize'
API_VERSION = 'v1.0'
ACCESS_TOKEN_TTL = 3600  # 60 minutes
REFRESH_TOKEN_TTL = 604800  # 1 week
KNOWN_PREFIXES = [
    URL_PREFIX,
    '/rcvideo',
    '/video',
    '/webinar',
    '/analytics',
    '/ai',
    '/team-messaging',
    '/scim',
    '/cx/'
]


class Platform(Observable):
    def __init__(self, client, key='', secret='', server='', name='', version='', redirect_uri='',
                 known_prefixes=None):

        Observable.__init__(self)
        if(server == None):
            raise Exception("SDK init error: RINGCENTRAL_SERVER_URL value not found.")
        if(key == None):
            raise Exception("SDK init error: RINGCENTRAL_CLIENT_ID value not found.")
        if(secret == None):
            raise Exception("SDK init error: RINGCENTRAL_CLIENT_SECRET value not found.")

        self._server = server
        self._key = key
        self._name = name if name else 'Unnamed'
        self._version = version if version else '0.0.0'
        self._redirect_uri = redirect_uri
        self._secret = secret
        self._client = client
        self._auth = Auth()
        self._account = ACCOUNT_ID
        self._known_prefixes = known_prefixes if known_prefixes else KNOWN_PREFIXES
        self._userAgent = ((self._name + ('/' + self._version if self._version else '') + ' ') if self._name else '') + \
                          sys.platform + '/VERSION' + ' ' + \
                          'PYTHON/VERSION ' + \
                          'RCPYTHONSDK/VERSION'

    def auth(self):
        return self._auth

    def create_url(self, url, add_server=False, add_method=None, add_token=False):
        """
            Creates a complete URL based on the provided URL and additional parameters.

            Args:
                url (str): The base URL.
                add_server (bool): Whether to prepend the server URL if the provided URL doesn't contain 'http://' or 'https://'.
                add_method (str, optional): The HTTP method to append as a query parameter.
                add_token (bool): Whether to append the access token as a query parameter.

            Returns:
                str: The complete URL.

            Note:
                - If `add_server` is True and the provided URL doesn't start with 'http://' or 'https://', the server URL will be prepended.
                - If the provided URL doesn't contain known prefixes or 'http://' or 'https://', the URL_PREFIX and API_VERSION will be appended.
                - If the provided URL contains ACCOUNT_PREFIX followed by ACCOUNT_ID, it will be replaced with ACCOUNT_PREFIX and the account ID associated with the SDK instance.
                - If `add_method` is provided, it will be appended as a query parameter '_method'.
                - If `add_token` is True, the access token associated with the SDK instance will be appended as a query parameter 'access_token'.
        """
        built_url = ''
        has_http = url.startswith('http://') or url.startswith('https://')

        if add_server and not has_http:
            built_url += self._server

        if not reduce(lambda res, prefix: res if res else url.find(prefix) == 0, self._known_prefixes, False) and not has_http:
            built_url += URL_PREFIX + '/' + API_VERSION

        if url.find(ACCOUNT_PREFIX) >= 0:
            built_url = built_url.replace(ACCOUNT_PREFIX + ACCOUNT_ID, ACCOUNT_PREFIX + self._account)

        built_url += url

        if add_method:
            built_url += ('&' if built_url.find('?') >= 0 else '?') + '_method=' + add_method

        if add_token:
            built_url += ('&' if built_url.find('?') >= 0 else '?') + 'access_token=' + self._auth.access_token()

        return built_url

    def logged_in(self):
        """
        Checks if the user is currently logged in.

        Returns:
            bool: True if the user is logged in, False otherwise.

        Note:
            - This method checks if the access token is valid.
            - If the access token is not valid, it attempts to refresh it by calling the `refresh` method.
            - If any exceptions occur during the process, it returns False.
        """
        try:
            return self._auth.access_token_valid() or self.refresh()
        except:
            return False

    def login_url(self, redirect_uri, state='', challenge='', challenge_method='S256'):
        """
        Generates the URL for initiating the login process.

        Args:
            redirect_uri (str): The URI to which the user will be redirected after authentication.
            state (str, optional): A value to maintain state between the request and the callback. Default is ''.
            challenge (str, optional): The code challenge for PKCE (Proof Key for Code Exchange). Default is ''.
            challenge_method (str, optional): The code challenge method for PKCE. Default is 'S256'.

        Returns:
            str: The login URL.
        """
        built_url = self.create_url( AUTHORIZE_ENDPOINT, add_server=True )
        built_url += '?response_type=code&client_id=' + self._key + '&redirect_uri=' + urllib.parse.quote(redirect_uri)
        if state:
            built_url += '&state=' + urllib.parse.quote(state)
        if challenge:
            built_url += '&code_challenge=' + urllib.parse.quote(challenge) + '&code_challenge_method=' + challenge_method
        return built_url

    def login(self, username='', extension='', password='', code='', redirect_uri='', jwt='', verifier=''):
        """
            Logs in the user using various authentication methods.

            Args:
                username (str, optional): The username for authentication. Required if password is provided. Default is ''.
                extension (str, optional): The extension associated with the username. Default is ''.
                password (str, optional): The password for authentication. Required if username is provided. Default is ''.
                code (str, optional): The authorization code for authentication. Default is ''.
                redirect_uri (str, optional): The URI to redirect to after authentication. Default is ''.
                jwt (str, optional): The JWT (JSON Web Token) for authentication. Default is ''.
                verifier (str, optional): The code verifier for PKCE (Proof Key for Code Exchange). Default is ''.

            Returns:
                Response: The response object containing authentication data if successful.

            Raises:
                Exception: If the login attempt fails or invalid parameters are provided.

            Note:
                - This method supports multiple authentication flows including password-based, authorization code, and JWT.
                - It checks for the presence of required parameters and raises an exception if necessary.
                - Deprecation warning is issued for username-password login; recommend using JWT or OAuth instead.
                - Constructs the appropriate request body based on the provided parameters.
                - Uses `create_url` to build the token endpoint URL, adding the server URL if required.
                - Sends the authentication request using `_request_token`.
                - Triggers the loginSuccess or loginError event based on the outcome of the login attempt.
        """
        try:
            if not code and not username and not password and not jwt:
                raise Exception('Either code, or username with password, or jwt has to be provided')
            if username and password:
                warnings.warn("username-password login will soon be deprecated. Please use jwt or OAuth instead.")
            if not code and not jwt:
                body = {
                    'grant_type': 'password',
                    'username': username,
                    'password': password,
                    'access_token_ttl': ACCESS_TOKEN_TTL,
                    'refresh_token_ttl': REFRESH_TOKEN_TTL
                }
                if extension:
                    body['extension'] = extension
            elif jwt:
                body = {
                    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                    'assertion': jwt
                }
            else:
                body = {
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri if redirect_uri else self._redirect_uri,
                    'code': code
                }
                if verifier:
                    body['code_verifier'] = verifier

            built_url = self.create_url( TOKEN_ENDPOINT, add_server=True )
            response = self._request_token( built_url, body=body)
            self._auth.set_data(response.json_dict())
            self.trigger(Events.loginSuccess, response)
            return response
        except Exception as e:
            self.trigger(Events.loginError, e)
            raise e

    def refresh(self):
        """
            Refreshes the authentication tokens.

            Returns:
                Response: The response object containing refreshed authentication data if successful.

            Raises:
                Exception: If the refresh token has expired or if any error occurs during the refresh process.

            Note:
                - This method checks if the refresh token is still valid using `_auth.refresh_token_valid()`.
                - Constructs the request body with the grant type as 'refresh_token' and includes the refresh token.
                - Sends the token refresh request using `_request_token` at this '/restapi/oauth/token end point.
                - Triggers the refreshSuccess or refreshError event based on the outcome of the refresh attempt.
        """
        try:
            if not self._auth.refresh_token_valid():
                raise Exception('Refresh token has expired')
            response = self._request_token(TOKEN_ENDPOINT, body={
                'grant_type': 'refresh_token',
                'refresh_token': self._auth.refresh_token(),
                'access_token_ttl': ACCESS_TOKEN_TTL,
                'refresh_token_ttl': REFRESH_TOKEN_TTL
            })
            self._auth.set_data(response.json_dict())
            self.trigger(Events.refreshSuccess, response)
            return response
        except Exception as e:
            self.trigger(Events.refreshError, e)
            raise e

    def logout(self):
        """
            Logs out the user by revoking the access token.

            Returns:
                Response: The response object containing logout confirmation if successful.

            Raises:
                Exception: If any error occurs during the logout process.

            Note:
                - Constructs the request body with the access token to be revoked.
                - Sends the token revoke request using `_request_token` at this /restapi/oauth/revoke end point.
                - Resets the authentication data using `_auth.reset()` upon successful logout.
                - Triggers the logoutSuccess or logoutError event based on the outcome of the logout attempt.
        """
        try:
            response = self._request_token(REVOKE_ENDPOINT, body={
                'token': self._auth.access_token()
            })
            self._auth.reset()
            self.trigger(Events.logoutSuccess, response)
            return response
        except Exception as e:
            self.trigger(Events.logoutError, e)
            raise e

    def inflate_request(self, request, skip_auth_check=False):
        """
            Inflates the provided request object with necessary headers and URL modifications.

            Args:
                request (Request): The request object to be inflated.
                skip_auth_check (bool, optional): Whether to skip the authentication check and header addition. Default is False.

            Note:
                - If `skip_auth_check` is False (default), it ensures authentication by calling `_ensure_authentication` and adds the 'Authorization' header.
                - Sets the 'User-Agent' and 'X-User-Agent' headers to the value specified in `_userAgent`.
                - Modifies the request URL using `create_url`, adding the server URL if necessary.
        """
        if not skip_auth_check:
            self._ensure_authentication()
            request.headers['Authorization'] = self._auth_header()

        request.headers['User-Agent'] = self._userAgent
        request.headers['X-User-Agent'] = self._userAgent
        request.url = self.create_url(request.url, add_server=True)

        return request

    def send_request(self, request, skip_auth_check=False):
        return self._client.send(self.inflate_request(request, skip_auth_check=skip_auth_check))

    def get(self, url, query_params=None, headers=None, skip_auth_check=False):
        request = self._client.create_request('GET', url, query_params=query_params, headers=headers)
        return self.send_request(request, skip_auth_check=skip_auth_check)

    def post(self, url, body=None, query_params=None, headers=None, skip_auth_check=False):
        request = self._client.create_request('POST', url, query_params=query_params, headers=headers, body=body)
        return self.send_request(request, skip_auth_check=skip_auth_check)

    def put(self, url, body=None, query_params=None, headers=None, skip_auth_check=False):
        request = self._client.create_request('PUT', url, query_params=query_params, headers=headers, body=body)
        return self.send_request(request, skip_auth_check=skip_auth_check)

    def patch(self, url, body=None, query_params=None, headers=None, skip_auth_check=False):
        request = self._client.create_request('PATCH', url, query_params=query_params, headers=headers, body=body)
        return self.send_request(request, skip_auth_check=skip_auth_check)

    def delete(self, url, body=None, query_params=None, headers=None, skip_auth_check=False):
        request = self._client.create_request('DELETE', url, query_params=query_params, headers=headers, body=body)
        return self.send_request(request, skip_auth_check=skip_auth_check)

    def _request_token(self, path='', body=None):
        headers = {
            'Authorization': 'Basic ' + self._api_key(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        request = self._client.create_request('POST', path, body=body, headers=headers)
        return self.send_request(request, skip_auth_check=True)

    def _api_key(self):
        return base64encode(self._key + ':' + self._secret)

    def _auth_header(self):
        return self._auth.token_type() + ' ' + self._auth.access_token()

    def _ensure_authentication(self):
        if not self._auth.access_token_valid():
            self.refresh()
