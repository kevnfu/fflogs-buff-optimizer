import oauthlib.oauth2 as oauth2
from requests_oauthlib import OAuth2Session
# from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from math import floor

from gql import gql
from gql import Client as GQLClient
from gql.transport.requests import RequestsHTTPTransport

from config import CLIENT_ID, CLIENT_SECRET

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
                bosses: actors(subType: "Boss") {{
                    id
                    name
                }}
                players: actors(type: "Player") {{
                    id
                    name
                }}
            }}
            startTime
            endTime
            fights (encounterID: {encounterID}) {{
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
            events(dataType: Deaths, limit: 10000, startTime: {startTime}, endTime: {endTime}) {{
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
                hostilityType: Friendlies, limit: 10000, 
                startTime: {startTime}, endTime: {endTime}) {{
                data
                nextPageTimestamp
            }}
        }}
    }}
}}

"""

Q_DEATHS_OVERKILLS = """
query {{
    reportData {{
        report(code: "{reportCode}") {{
            deaths: events(dataType: Deaths, limit: 10000, startTime: {startTime}, endTime: {endTime}) {{
                data
                nextPageTimestamp
            }}
            overkills: events(dataType: DamageDone, filterExpression: "overkill > 0",
                hostilityType: Friendlies, limit: 10000, 
                startTime: {startTime}, endTime: {endTime}) {{
                data
                nextPageTimestamp
            }}
        }}
    }}
}}
"""

Q_ENCOUNTER = """
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

class Encounter(Enum):
    DSU = 1065

@dataclass 
class Report:
    code: str
    title: str
    startTime: int
    endTime: int
    bosses: dict()
    players: dict()
    fights: list()
    overkills: list()
    deaths: list()


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

class FFClient:
    CLIENT_API_URL = 'https://www.fflogs.com/api/v2/client'
    OAUTH_TOKEN_URL = 'https://www.fflogs.com/oauth/token'

    def __init__(self, client_id: str, secret: str) -> None:
        client = oauth2.BackendApplicationClient(client_id)
        session = OAuth2Session(client=client)
        token = session.fetch_token(
            self.OAUTH_TOKEN_URL,
            client_id=client_id,
            client_secret=secret
        )

        self.access_token = token['access_token']

        transport = RequestsHTTPTransport(url=self.CLIENT_API_URL)
        transport.headers = {'Authorization': f'Bearer {self.access_token}'}

        self.client = GQLClient(transport=transport, fetch_schema_from_transport=True)

    def q(self, query: str):
        return self.client.execute(gql(query))

    def report(self, code: str) -> Report:
        res = self.q(Q_REPORT.format(reportCode=reportCode,encounterID=Encounter.DSU.value))
        report = res['reportData']['report']

        master = report['masterData']
        bosses = {actor['id']: actor['name'] for actor in master['bosses']}
        players = {actor['id']: actor['name'] for actor in master['players']}

        res = self.q(Q_DEATHS_OVERKILLS.format(
            reportCode=code,
            startTime=report['fights'][0]['startTime'],
            endTime=report['fights'][-1]['endTime']))
        overkills = res['reportData']['report']['overkills']['data']
        deaths = res['reportData']['report']['deaths']['data']

        fights = list()
        for fight in report['fights']:
            fights.append(Fight(
                i=fight['id'],
                encounterID=fight['encounterID'],
                startTime=fight['startTime'],
                endTime=fight['endTime'],
                percent=fight['fightPercentage'],
                lastPhase=fight['lastPhaseAsAbsoluteIndex']
            ))

        return Report(
            code=code,
            title=report['title'],
            startTime=report['startTime'],
            endTime=report['endTime'],
            bosses=bosses,
            players=players,
            fights=fights,
            overkills=overkills,
            deaths=deaths
        )

@dataclass
class Deaths:
    code: int
    time: int
    name: str
    fightID: int

    def __init__(self, json, report):
        self.code = json['targetID']
        self.time = json['timestamp']
        self.name = report.bosses.get(self.code, str(self.code))
        self.fightID = json['fight']

    def __str__(self):
        return f'{self.time}: {self.name} died Pull: {self.fightID}'



def from_ms(ms: int) -> str:
    hour = floor(ms/(1000*60*60) % 24)
    minute = floor(ms/(1000*60) % 60)
    second = floor(ms/(1000) % 60)
    return f'{hour:02.0f}:{minute:02.0f}:{second:02.0f}'

def to_ms(timestr: str) -> int:
    minutes, seconds = timestr.split(':')
    return int(minutes)*1000*60 + int(seconds)*1000

def print_timestamps(report, timestr, ref_fight=0):
    offset = to_ms(timestr) - report.fights[ref_fight].startTime
    print('00:00 Start')
    for fight in report.fights:
        # print(from_ms(fight.startTime-report.fights[0].startTime))
        print(f'{from_ms(fight.startTime + offset)} Pull {fight.i} Phase {fight.lastPhase}')

    print(f'\nhttps://www.fflogs.com/reports/{report.code}')

def print_twitch(report, url, timestr, ref_fight=0):
    offset = to_ms(timestr) - report.fights[ref_fight].startTime
    for fight in report.fights:
        # print(from_ms(fight.startTime-report.fights[0].startTime))
        if fight.encounterID != 1065: continue
        ms = fight.startTime + offset
        minutes = floor(ms/(1000*60))
        seconds = floor(ms/(1000) % 60)
        print(f'{url}?t={minutes}m{seconds}s Pull {fight.i} Phase {fight.lastPhase} ')

def fight_phases(report):
    print(report.overkills)

# reportCode = "XZdRqnWAPBGQf3jg"
# reportCode = "7WtwbQyvpFDA2RhZ"
reportCode = "rHq4kRnmKcbpgwZY"
# reportCode = "PkaMGFgDf7hBWn2p"

client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = client.report(reportCode)

fight_phases(report)


# phase 1 start -> Ser Adelphel/Grinnaux gone -> Pure of heart damage?
# phase 2 start -> King thordan overkill
# phase 3 P2 end/Final Chorus damage -> Nidhogg overkill
# phase 4 P3 end/soul of friendship buff -> Eyes overkill
# Intermission P4 end -> spear of the fury overkill
# phase 5