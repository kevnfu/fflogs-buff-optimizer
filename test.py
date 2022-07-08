import oauthlib.oauth2 as oauth2
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

from gql import gql
from gql import Client as GQLClient
from gql.transport.requests import RequestsHTTPTransport

from config import CLIENT_ID, CLIENT_SECRET

CLIENT_API_URL = 'https://www.fflogs.com/api/v2/client'
OAUTH_TOKEN_URL = 'https://www.fflogs.com/oauth/token'

Q_FIGHTDATA = """
query {{
    reportData {{
        report(code: "{reportCode}") {{
            # fights {{
            #     startTime, endTime
            # }}
            table(startTime: 343855, endTime: 472491)

        }}
    }}
}}
"""

reportCode = "19X6CgBFYLKZzMNJ"
fightID = "50"

# auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
client = oauth2.BackendApplicationClient(CLIENT_ID)
session = OAuth2Session(client=client)

token = session.fetch_token(
    OAUTH_TOKEN_URL,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

print(token)

access_token = token['access_token']

transport = RequestsHTTPTransport(url=CLIENT_API_URL)
transport.headers = {'Authorization': f'Bearer {access_token}'}

gql_client = GQLClient(transport=transport, fetch_schema_from_transport=True)

gql_q = gql(Q_FIGHTDATA.format(reportCode=reportCode, fightID=fightID))

x = gql_client.execute(gql_q)

print(x)
