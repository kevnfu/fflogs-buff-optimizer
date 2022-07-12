import oauthlib.oauth2 as oauth2
from requests_oauthlib import OAuth2Session
# from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
from dataclasses import dataclass

from gql import gql
from gql import Client as GQLClient
from gql.transport.requests import RequestsHTTPTransport

from config import CLIENT_ID, CLIENT_SECRET

CLIENT_API_URL = 'https://www.fflogs.com/api/v2/client'
OAUTH_TOKEN_URL = 'https://www.fflogs.com/oauth/token'

Q_REPORT = """
query {{
    reportData {{
        report(code: "{reportCode}") {{
            title
            masterData {{
                actors(subType: "Boss") {{
                    id
                    name
                    subType
                }}
            }}
            startTime
            endTime
            fights {{
                id
                encounterID
                startTime
                endTime
            }}
        }}
    }}
}}
"""

Q_EVENTS = """
query {{
    reportData {{
        report(code: "{reportCode}") {{
            events(filterExpression: "inCategory('deaths') = true", startTime: 8984334, endTime: 9448023) {{
                data
                nextPageTimestamp
            }}
        }}
    }}
}}

"""

Q_ENCOUNTER= """
query {{
    worldData {{
        encounter(id: {encounterID}) {{
            zone {{
                name
            }}
        }}
    }}
}}
"""

reportCode = "fj1tvmxZhWa2zKHd"
fightID = "1"

# auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
client = oauth2.BackendApplicationClient(CLIENT_ID)
session = OAuth2Session(client=client)

token = session.fetch_token(
    OAUTH_TOKEN_URL,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

# print(token)

access_token = token['access_token']

transport = RequestsHTTPTransport(url=CLIENT_API_URL)
transport.headers = {'Authorization': f'Bearer {access_token}'}

gql_client = GQLClient(transport=transport, fetch_schema_from_transport=True)

gql_q = gql(Q_REPORT.format(reportCode=reportCode))

res = gql_client.execute(gql_q)

report = res['reportData']['report']

bosses = report['masterData']['actors']
startTime = report['startTime']
endTime = report['endTime']
fights = report['fights']

for fight in fights:
    print(fight)

gql_q = gql(Q_ENCOUNTER.format(encounterID=1065))
res = gql_client.execute(gql_q)
print(res)


# print(json.dumps(report, indent=4))
time = report['startTime'] / 1000 + 18016083/1000
# print(time)
print(datetime.fromtimestamp(time).strftime('%H:%M:%S'))

@dataclass 
class Report:
    code: str
    title: str
    startTime: int
    endTime: int
    bosses: dict()
    fights: list()

@dataclass
class Fight:
    """docstring for Fight"""
    i: int
    encounterID: int
    startTime: int
    endTime: int
    # report: Report

    def __init__(self, json):
        self.i = json['id']
        self.encounterID = json['encounterID']
        self.startTime = json['startTime']
        self.endTime = json['endTime']


@dataclass
class Bosses:
    code: int
    name: str


def get_report(code):
    res = gql_client.execute(gql(Q_REPORT.format(reportCode=reportCode)))
    report = res['reportData']['report']
    return Report(
        code=code,
        title=report['title'],
        startTime=report['startTime'],
        endTime=report['endTime'],
        bosses=report['masterData']['actors'],
        fights=list(map(Fight, report['fights']))
    )

print(get_report(reportCode))