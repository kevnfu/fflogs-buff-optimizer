import oauthlib.oauth2 as oauth2
from requests_oauthlib import OAuth2Session
# from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
from dataclasses import dataclass

from math import floor

from gql import gql
from gql import Client as GQLClient
from gql.transport.requests import RequestsHTTPTransport

from config import CLIENT_ID, CLIENT_SECRET

CLIENT_API_URL = 'https://www.fflogs.com/api/v2/client'
OAUTH_TOKEN_URL = 'https://www.fflogs.com/oauth/token'

Q_REPORT = """
query {{
    rateLimitData {{
        limitPerHour
        pointsSpentThisHour
    }}
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
                fightPercentage
                lastPhaseAsAbsoluteIndex
            }}
        }}
    }}
}}
"""

Q_DEATHS = """
query {{
    reportData {{
        report(code: "{reportCode}") {{
            # filterExpression: "inCategory('deaths')=true"
            events(dataType: Deaths, hostilityType: Enemies, limit: 10000, startTime: {startTime}, endTime: {endTime}) {{
                data
                nextPageTimestamp
            }}
        }}
    }}
}}

"""

Q_OVERKILL = """
query {{
    reportData {{
        report(code: "{reportCode}") {{
            events(dataType: DamageDone, filterExpression: "overkill > 0",
                hostilityType: Friendlies, limit: 10000, startTime: {startTime}, endTime: {endTime}) {{
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

# reportCode = "XZdRqnWAPBGQf3jg"
# reportCode = "7WtwbQyvpFDA2RhZ"
reportCode = "rHq4kRnmKcbpgwZY"

# auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
client = oauth2.BackendApplicationClient(CLIENT_ID)
session = OAuth2Session(client=client)

token = session.fetch_token(
    OAUTH_TOKEN_URL,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

access_token = token['access_token']

transport = RequestsHTTPTransport(url=CLIENT_API_URL)
transport.headers = {'Authorization': f'Bearer {access_token}'}

gql_client = GQLClient(transport=transport, fetch_schema_from_transport=True)

# time = report['startTime'] / 1000 + 18016083/1000
# print(datetime.fromtimestamp(time).strftime('%H:%M:%S'))

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
    percent: float
    lastPhase: int
    # report: Report

    def __init__(self, json):
        self.i = json['id']
        self.encounterID = json['encounterID']
        self.startTime = json['startTime']
        self.endTime = json['endTime']
        self.percent = json['fightPercentage']
        self.lastPhase = json['lastPhaseAsAbsoluteIndex']


@dataclass
class Bosses:
    code: int
    name: str

@dataclass
class Deaths:
    code: int
    time: int
    name: str
    fightID: int

    def __init__(self, json, report):
        self.code = json['targetID']
        self.time = json['timestamp']
        self.name = report.bosses[self.code]
        self.fightID = json['fight']

    def __str__(self):
        return f'{self.time}: {self.name} died Pull: {self.fightID}'

def get_report(code):
    res = gql_client.execute(gql(Q_REPORT.format(reportCode=reportCode)))
    # print(json.dumps(res, indent=4))
    report = res['reportData']['report']
    bosses = dict()
    bosses = {actor['id']: actor['name'] for actor in report['masterData']['actors'] if actor['subType'] == 'Boss'}
    return Report(
        code=code,
        title=report['title'],
        startTime=report['startTime'],
        endTime=report['endTime'],
        bosses=bosses,
        fights=list(map(Fight, report['fights']))
    )

def from_ms(ms: int) -> str:
    hour = floor(ms/(1000*60*60) % 24)
    minute = floor(ms/(1000*60) % 60)
    second = floor(ms/(1000) % 60)
    return f'{hour:02.0f}:{minute:02.0f}:{second:02.0f}'

def to_ms(hour, minute, second) -> int:
    return hour*1000*60*60 + minute*1000*60 + second*1000

def get_death_events(report):
    res = gql_client.execute(gql(Q_DEATHS.format(
        reportCode=report.code,
        startTime=report.fights[0].startTime,
        endTime=report.fights[-1].endTime)))
    # print(res)
    # {10: 'Ser Adelphel', 11: 'Ser Grinnaux', 15: 'Ser Charibert', 22: 'spear of the Fury', 23: 'King Thordan', 39: 'Nidhogg', 42: 'left eye', 43: 'right eye', 52: 'King Thordan'}
    for event in res['reportData']['report']['events']['data']:
        print(str(Deaths(event, report)))

def print_timestamps(report, timestr, ref_fight=0):
    minutes, seconds = timestr.split(':')
    offset = (int(minutes)*60 + int(seconds))*1000 - report.fights[ref_fight].startTime
    print('00:00 Start')
    for fight in report.fights:
        # print(from_ms(fight.startTime-report.fights[0].startTime))
        if fight.encounterID != 1065: continue
        print(f'{from_ms(fight.startTime + offset)} Pull {fight.i} Phase {fight.lastPhase}')

    print(f'\nhttps://www.fflogs.com/reports/{report.code}')

def print_twitch(report, url, timestr, ref_fight=0):
    minutes, seconds = timestr.split(':')
    offset = (int(minutes)*60 + int(seconds))*1000 - report.fights[ref_fight].startTime
    for fight in report.fights:
        # print(from_ms(fight.startTime-report.fights[0].startTime))
        if fight.encounterID != 1065: continue
        ms = fight.startTime + offset
        minutes = floor(ms/(1000*60))
        seconds = floor(ms/(1000) % 60)
        print(f'{url}?t={minutes}m{seconds}s Pull {fight.i} Phase {fight.lastPhase} ')

def get_overkill(report):
    res = gql_client.execute(gql(Q_OVERKILL.format(
        reportCode=report.code,
        startTime=report.fights[0].startTime,
        endTime=report.fights[-1].endTime)))

    data = res['reportData']['report']['events']['data']

    for event in data:
        # if event['targetID'] in report.bosses:
        print(report.bosses[event['targetID']])
        print(event)

report = get_report(reportCode)
# print_timestamps(report, '07:35')
# print_twitch(report, 'https://www.twitch.tv/videos/1530252131', '02:02')

get_overkill(report)

# print(report.bosses)
# get_events(report)

# phase 1 start -> Ser Adelphel/Grinnaux gone -> Pure of heart damage?
# phase 2 start -> King thordan overkill
# phase 3 P2 end/Final Chorus damage -> Nidhogg overkill
# phase 4 P3 end/soul of friendship buff -> Eyes overkill
# Intermission P4 end -> spear of the fury overkill
# phase 5