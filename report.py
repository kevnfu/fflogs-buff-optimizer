from __future__ import annotations
from typing import List, Dict, Tuple, Iterator, Any

# standard
import json
from dataclasses import dataclass
from math import floor

# custom
from enums import Encounter, Platform
from queries import Q_MASTER_DATA, Q_FIGHTS, Q_EVENTS
from events import Event, EventList

@dataclass
class Actor:
    i: int
    name: str
    gameID: int
    type_: str
    subtype: str

    def __init__(self, data: Dict[str: Any]) -> None:
        self.i = data['id']
        self.name = data['name']
        self.gameID = data['gameID']
        self.type_ = data['type']
        self.subtype = data['subType']

@dataclass
class Ability:
    i: int
    name: str

    def __init__(self, data: Dict[str: Any]) -> None:
        self.i = data['gameID']
        self.name = data['name']

    
class Fight:
    i: int
    encounter: int
    start_time: int
    end_time: int
    percent: float
    lastPhase: int
    report: Report

    def __init__(self, data: Dict[str, Any], report: Report) -> None:
        self.i=data['id']
        self.encounter=data['encounterID']
        self.start_time=data['startTime']
        self.end_time=data['endTime']
        self.percent=data['fightPercentage']
        self.lastPhase=data['lastPhaseAsAbsoluteIndex']
        self.report=report

class Report:
    """Report for one type of encounter"""
    def __init__(self, code: str, client: 'FFClient', encounter: Encounter) -> None:
        self._client = client
        self.code = code
        self.encounter = encounter
        self.data = dict() # to be filled w/ individual calls

        self._fetch_master_data() # self.r_start_time, r_end_time
        self._fetch_fights() # self.fights, start_time, end_time

    def _fetch_master_data(self) -> None:
        res = self._client.q(Q_MASTER_DATA, {
            'reportCode': self.code})
        report = res['reportData']['report']
        self.title = report['title']
        self.owner = report['owner']
        self.guild = report['guild']
        self.r_start_time = report['startTime']
        self.r_end_time = report['endTime']

        with open('master.json', 'w') as f:
            f.write(json.dumps(res, indent=4))
        with open('actors.json', 'w') as f:
            f.write(json.dumps(report['masterData']['actors'], indent=4))
        with open('abilites.json', 'w') as f:
            f.write(json.dumps(report['masterData']['abilities'], indent=4))

        self.actors = [Actor(a) for a in report['masterData']['actors']]
        # self.actors_by_id = {a.i: a for a in self.actors}

        self.abilities = [Ability(a) for a in report['masterData']['abilities']]
        # self.abilities_by_id = {a.i: a for a in self.abilities}
        # self.abilities_by_name = {a.name: a for a in self.abilities}

    def _fetch_fights(self) -> None:
        res = self._client.q(Q_FIGHTS, {
            'reportCode': self.code,
            'encounterID': self.encounter.value})
        report = res['reportData']['report']

        # fight data
        self.fights = [Fight(data, self) for data in report['fights']]
        self.fights_by_id = {f.i: f for f in self.fights}
        # startTime and endTime are relative to the report, not unix time
        self.start_time = self.fights[0].start_time
        self.end_time = self.fights[-1].end_time

    # get child elements
    def get_fight(self, fightID: int) -> Fight:
        return next(filter(lambda x: x.i==fightID, self.fights))

    def get_actor(self, name: str) -> List[Actor]:
        return next(filter(lambda a: a.name == name, self.actors))

    def get_actor_ids(self, name: str) -> List[int]:
        return [a.i for a in self.actors if a.name == name]

    def get_ability(self, name) -> Ability:
        return next(filter(lambda a: a.name == name, self.abilities))

    def _fetch_events(self, filter_expression: str='', fight_ids: List[Int]=[]) -> EventList:
        start_time = self.start_time
        all_events = []
        while start_time:
            res = self._client.q(Q_EVENTS, params={
                'reportCode': self.code,
                'encounterID': self.encounter.value,
                'startTime': start_time, 
                'endTime': self.end_time,
                'filter': filter_expression,
                'fightIDs': fight_ids})
            events = res['reportData']['report']['events']
            all_events += [*map(Event, events['data'])]
            start_time = events['nextPageTimestamp']

        with open('test.json', 'w') as f:
            for e in all_events:
                f.write(str(e) + '\n')

        return EventList(all_events, self)

    def deaths(self) -> EventList:
        return self._fetch_events("inCategory('deaths') = true")

    def actions(self, ability_name: str, actor_name: str='') -> EventList:
        filter_str = f"type='cast' AND ability.name='{ability_name}'"
        if actor_name:
            filter_str += f" AND source.name='{actor_name}'"
        return self._fetch_events(filter_str)

    def dummy_downs(self) -> EventList:
        return self._fetch_events("type='applydebuff' AND target.disposition='friendly' AND ability.name='Damage Down'")

    # outputs:
    def set_video_offset_time(self, mmss: str, fightID: int) -> Report:
        """Put in timestamp of video at Fight fightID"""
        minutes, seconds = mmss.split(':')
        ms = int(minutes)*1000*60 + int(seconds)*1000

        fight = self.get_fight(fightID)
        self.offset = ms - fight.start_time
        return self

    def _relative_time(self, time: int) -> Tuple(int, int, int):
        """Takes event time and outputs video time"""
        ms = time + self.offset
        hour = floor(ms/(1000*60*60) % 24)
        minute = floor(ms/(1000*60) % 60)
        second = floor(ms/(1000) % 60)
        return hour, minute, second

    @staticmethod
    def _youtube_time(time: int) -> str:
        hour, minute, second = time
        return f'{hour:02.0f}:{minute:02.0f}:{second:02.0f}'

    @staticmethod
    def _twitch_url(time: int, code: str) -> str:
        hour, minute, second = time
        minute += hour * 60
        return f'https://www.twitch.tv/videos/{code}?t={minute}m{second}s'

    def set_output_type(self, output_type: Platform, code: str=None) -> Report:
        self.output_type = output_type
        self.output_code = code
        return self

    def _to_output(self, time: int) -> str:
        assert self.output_type is not None, 'No output_type selected.'

        match self.output_type:
            case Platform.YOUTUBE:
                return self._youtube_time(time)
            case Platform.TWITCH:
                assert self.output_code is not None
                return self._twitch_url(time, self.output_code)
            case _:
                raise ValueError('Not a supported platform')

