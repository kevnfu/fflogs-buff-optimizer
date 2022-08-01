from __future__ import annotations, with_statement

import oauthlib.oauth2 as oauth2
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

from gql import gql
from gql import Client as GQLClient
from gql.transport.requests import RequestsHTTPTransport

import json
# from io import StringIO
from copy import deepcopy
import os


class FFClient:
    CLIENT_API_URL = 'https://www.fflogs.com/api/v2/client'
    OAUTH_TOKEN_URL = 'https://www.fflogs.com/oauth/token'
    CACHE_DIR = './querycache'

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._auth = HTTPBasicAuth(client_id, client_secret)
        client = oauth2.BackendApplicationClient(client_id)
        self._session = OAuth2Session(client=client)
        self._transport = RequestsHTTPTransport(url=self.CLIENT_API_URL)
        self._client = GQLClient(transport=self._transport, fetch_schema_from_transport=True)

        self._cache = {}
        self.load_cache()
        self.refresh_token()

    def refresh_token(self) -> FFClient:
        token = self._session.fetch_token(
            self.OAUTH_TOKEN_URL,
            auth=self._auth
        )
        access_token = token['access_token']
        self._transport.headers = {'Authorization': f'Bearer {access_token}'}
        return self

    def q(self, query: str, params: dict) -> dict:
        key = query + json.dumps(params)
        if key not in self._cache:
            res = self._client.execute(gql(query), variable_values=params)
            print(res.get('rateLimitData', 'no rateLimitData'))
            self._cache[key] = res

        return deepcopy(self._cache[key])

    def save_cache(self) -> None:
        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR)

        cache_path = os.path.join(self.CACHE_DIR, 'cache.json')

        with open(cache_path, 'w') as f:
            json.dump(self._cache, f)

    def load_cache(self) -> None:
        if not os.path.exists(self.CACHE_DIR):
            return

        cache_path = os.path.join(self.CACHE_DIR, 'cache.json')

        try:
            with open(cache_path, 'r') as f:
                self._cache = json.load(f)
        except FileNotFoundError:
            pass

    def clear_cache(self) -> None:
        cache_path = os.path.join(self.CACHE_DIR, 'cache.json')
        try:
            os.remove(cache_path)
        except OSError:
            pass

