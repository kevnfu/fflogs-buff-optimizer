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

        # cache is {reportcode: {params+query: res}}
        self._cache = {}
        self.refresh_token()

    def refresh_token(self) -> FFClient:
        token = self._session.fetch_token(
            self.OAUTH_TOKEN_URL,
            auth=self._auth
        )
        access_token = token['access_token']
        self._transport.headers = {'Authorization': f'Bearer {access_token}'}
        return self

    def _q(self, query: str, params: dict) -> dict:
        res = self._client.execute(gql(query), variable_values=params)
        print(res.get('rateLimitData', 'no rateLimitData'))
        return res

    def q(self, query: str, params: dict, *, cache: bool=True) -> dict:
        report_code = params.get('reportCode', None)
        if report_code is None or cache is False:
            return self._q(query, params)

        if report_code not in self._cache:
            self.load_cache(report_code)

        key = json.dumps(params) + query
        if key not in self._cache.setdefault(report_code, {}):
            self._cache[report_code][key] = self._q(query, params)

        return deepcopy(self._cache[report_code][key])

    def save_cache(self) -> None:
        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR)

        for report_code in self._cache:
            cache_path = os.path.join(self.CACHE_DIR, f'{report_code}.json')
            with open(cache_path, 'w') as f:
                json.dump(self._cache[report_code], f)

    def load_cache(self, report_code: str) -> bool:
        if not os.path.exists(self.CACHE_DIR):
            return False
        cache_path = os.path.join(self.CACHE_DIR, f'{report_code}.json')

        try:
            with open(cache_path, 'r') as f:
                self._cache[report_code] = json.load(f)
                return True
        except FileNotFoundError:
            # print(f"No cache for {report_code=}")
            # self._cache[report_code] = {}
            return False

    def clear_cache(self) -> None:
        cache_files = list(filter(
            lambda f: f.endswith('.json'),
            os.listdir(self.CACHE_DIR)
        ))

        for file in cache_files:
            try:
                os.remove(file)
            except OSError:
                pass

    # def master_data(self, report_code: str) -> dict:
    #     return self.q(Q_MASTER_DATA, {
    #         'reportCode': report_code
    #     })

    # def fights(self, report_code: str, encounter_id: int, fight_id: int=None) -> dict:
    #     return self.q(Q_FIGHTS, {
    #         'reportCode': report_code,
    #         'encounterID': encounter_id,
    #         'fightIDs': [fight_id]
    #         })

    # def events(self, report_code: int, encounter_id: int, start_time: int, end_time: int, fight_id: int) -> dict:
    #     return self.q(Q_EVENTS, {
    #         'reportCode': report_code,
    #         'encounterID': encounter_id,
    #         'startTime': start_time,
    #         'endTime': end_time,
    #         'fightIDs':[fight_id]
    #         })
