from __future__ import annotations

import oauthlib.oauth2 as oauth2
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

from gql import gql
from gql import Client as GQLClient
from gql.transport.requests import RequestsHTTPTransport


class FFClient:
    CLIENT_API_URL = 'https://www.fflogs.com/api/v2/client'
    OAUTH_TOKEN_URL = 'https://www.fflogs.com/oauth/token'

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._auth = HTTPBasicAuth(client_id, client_secret)
        client = oauth2.BackendApplicationClient(client_id)
        self._session = OAuth2Session(client=client)
        self._transport = RequestsHTTPTransport(url=self.CLIENT_API_URL)
        self._client = GQLClient(transport=self._transport, fetch_schema_from_transport=True)

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
        res = self._client.execute(gql(query), variable_values=params)
        print(res.get('rateLimitData', 'no rateLimitData'))
        return res
