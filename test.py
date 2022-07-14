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
query Report ($reportCode: String!, $encounterID: Int) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            title
            masterData {
                bosses: actors(subType: "Boss") {
                    id
                    name
                }
                players: actors(type: "Player") {
                    id
                    name
                }
                abilities {
                    gameID
                    name
                    # type
                }
            }
            startTime
            endTime
            fights (encounterID: $encounterID) {
                id
                encounterID
                startTime
                endTime
                fightPercentage
                lastPhaseAsAbsoluteIndex
            }
        }
    }
}
"""

Q_DEATHS = """
query Deaths {{
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
query DeathsAndOverkills ($reportCode: String!, $startTime: Float, $endTime: Float) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            deaths: events(dataType: Deaths, limit: 10000, startTime: $startTime, endTime: $endTime) {
                data
                nextPageTimestamp
            }
            overkills: events(dataType: DamageDone, filterExpression: "overkill > 0",
                hostilityType: Friendlies, limit: 10000, 
                startTime: $startTime, endTime: $endTime) {
                data
                nextPageTimestamp
            }
        }
    }
}
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

def print_json(x):
    print(json.dumps(x, indent=4))

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

    def __init__(self, data: dict) -> None:
        self.i=data['id']
        self.encounterID=data['encounterID']
        self.startTime=data['startTime']
        self.endTime=data['endTime']
        self.percent=data['fightPercentage']
        self.lastPhase=data['lastPhaseAsAbsoluteIndex']

@dataclass
class Death:
    targetID: int
    time: int
    fight: int
    sourceID: int
    abilityID: int

    def __init__(self, data: dict) -> None:
        self.time=data['timestamp']
        self.sourceID=data['sourceID']
        self.targetID=data['targetID']
        self.fight=data['fight']
        self.abilityID=data['abilityGameID']


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

        self._token = token['access_token']

        transport = RequestsHTTPTransport(url=self.CLIENT_API_URL)
        transport.headers = {'Authorization': f'Bearer {self._token}'}

        self._client = GQLClient(transport=transport, fetch_schema_from_transport=True)

    def q(self, query: str, params: dict) -> 'json':
        res = self._client.execute(gql(query), variable_values=params)
        # print(res['rateLimitData'])
        return res

class Report:
    def __init__(self, code: str, client: 'FFClient') -> None:
        self._client = client
        self._code = code
        self.fetch_data()

    def fetch_data(self) -> 'self':
        res = self._client.q(Q_REPORT, {
            'reportCode': self._code,
            'encounterID': Encounter.DSU.value})

        report = res['reportData']['report']

        # master data
        self.bosses = {actor['id']: actor['name'] for actor in report['masterData']['bosses']}
        self.players = {actor['id']: actor['name'] for actor in report['masterData']['players']}
        self.abilities = {ability['gameID']: ability['name'] for ability in report['masterData']['abilities']}

        # fight data
        self.fights = [Fight(data) for data in report['fights']]

        # deaths and overkills
        res = self._client.q(Q_DEATHS_OVERKILLS, {
            'reportCode': self._code,
            'startTime': self.fights[0].startTime,
            'endTime': self.fights[-1].endTime
            })

        overkills = res['reportData']['report']['overkills']['data']
        deaths = res['reportData']['report']['deaths']['data']
        # print_json(deaths)
        self.overkills = list(map(Death, overkills))
        self.deaths = list(map(Death, deaths))

        return self

    def relative_time(self, event):
        return

    def fight_phases(self):
        for fight in self.fights:
            # print(fight.i)
            boss_deaths = filter(lambda x: x.fight==fight.i, self.overkills)
            boss_names = list(map(lambda x: self.bosses[x.targetID], boss_deaths))
            print(boss_names)

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



# reportCode = "XZdRqnWAPBGQf3jg"
# reportCode = "7WtwbQyvpFDA2RhZ"
reportCode = "rHq4kRnmKcbpgwZY"
# reportCode = "PkaMGFgDf7hBWn2p"

client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = Report(reportCode, client)

report.fight_phases()

# print(report.deaths)
with open('output.txt', 'w') as f:
    f.write(json.dumps(report.abilities, indent=4))


# phase 1 start -> Ser Adelphel/Grinnaux gone -> Pure of heart damage?
# phase 2 start -> King thordan overkill
# phase 3 P2 end/Final Chorus damage -> Nidhogg overkill
# phase 4 P3 end/soul of friendship buff -> Eyes overkill
# Intermission P4 end -> spear of the fury overkill
# phase 5