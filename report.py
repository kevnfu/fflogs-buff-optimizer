from __future__ import annotations
from typing import Any

# standard
import json
from dataclasses import dataclass
from math import floor

# custom
from enums import Encounter, Platform
from queries import Q_MASTER_DATA, Q_FIGHTS, Q_EVENTS
from data import Event, EventList, Fight, Ability, Actor
from phases import PhaseModelDsu
from aura import AuraModel

class Report:
    """Report for one type of encounter"""
    def __init__(self, code: str, client: 'FFClient', encounter: Encounter) -> None:
        self._client = client
        self.code = code
        self.encounter = encounter
        match self.encounter:
            case Encounter.DSU: 
                self.pm = PhaseModelDsu(self)
            case Encounter.TEA:
                self.pm = PhaseModelTea(self)
            case _:
                raise NotImplementedError(f'No phase model for {self.encounter}')

        self.am = AuraModel(self)
        self.data = dict() # to be filled w/ individual calls

        self._fetch_master_data()
        self._fights = self._fetch_all_fights() # {fight id: fight}
        self._events = dict() # {fight id: EventList w/ all events}

    def _fetch_master_data(self) -> None:
        res = self._client.q(Q_MASTER_DATA, {
            'reportCode': self.code})
        report = res['reportData']['report']
        self.title = report['title']
        self.owner = report['owner']
        self.guild = report['guild']
        self.start_time = report['startTime']
        self.end_time = report['endTime']

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

    def _fetch_all_fights(self) -> list(Fight):
        res = self._client.q(Q_FIGHTS, {
            'reportCode': self.code,
            'encounterID': self.encounter.value})
        report = res['reportData']['report']
        report['fights']
        return {f['id']: Fight(f) for f in report['fights']}
        # self._fights_by_id = {f.i: f for f in self._fights}

    def _fetch_fight(self, fight_id: int) -> Fight:
        """Tries to obtain fight from the server"""
        res = self._client.q(Q_FIGHTS, {
            'reportCode': self.code,
            'encounterID': self.encounter.value,
            'fightIDs': [fight_id]})
        fight_list = res['reportData']['report']['fights']
        if fight_list: # if is not empty
            new_fight = Fight(fight_list[0])
            self._fights[new_fight.i] = new_fight
            return new_fight
        else:
            return None

    # get child elements
    def fight(self, fight_id: int) -> Fight:
        """Returns fight from self._fights, or tries to get from server"""
        if fight:=self._fights.get(fight_id, None):
            return fight
        elif fight:=self._fetch_fight(fight_id):
            self._fights[fight_id] = fight
            return fight
        else:
            return None

    def first_fight(self) -> Fight:
        return self._fights[min(self._fights.keys())]

    def last_fight(self) -> fights:
        return self._fights[max(self._fights.keys())]

    def get_actor(self, name_or_id: str | int) -> list[Actor] | Actor:
        if isinstance(name_or_id, str):
            return [a for a in self.actors if a.name==name_or_id]
        elif isinstance(name_or_id, int):
            return next(filter(lambda a: a.i==name_or_id, self.actors))
        else:
            raise TypeError(f'Needs a name or id, got {name_or_id=}')

    def get_actor_ids(self, name: str) -> list[int]:
        return [a.i for a in self.get_actor(name)]

    def get_ability(self, name_or_id: str | int) -> list[int] | str:
        if isinstance(name_or_id, str):
            return [a.i for a in self.abilities if a.name==name_or_id]
        elif isinstance(name_or_id, int):
            return next(filter(lambda a: a.i==name_or_id, self.abilities)).name
        else:
            raise TypeError(f'needs str or int, got {name_or_id=}')

    def _fetch_all_events(self, fight_id: int) -> EventList:
        fight = self.fight(fight_id)
        start_time = fight.start_time
        all_events = list()
        while start_time:
            res = self._client.q(Q_EVENTS, params={
                'reportCode': self.code,
                'encounterID': self.encounter.value,
                'startTime': start_time,
                'endTime': fight.end_time,
                'fightIDs': [fight_id]})
            events = res['reportData']['report']['events']
            all_events += [*map(Event, events['data'])]
            start_time = events['nextPageTimestamp']

        return EventList(all_events, self)

    def events(self, fight_id: int) -> EventList:
        if self.fight(fight_id) is None:
            return None
        if fight_id not in self._events:
            self._events[fight_id] = self._fetch_all_events(fight_id)
        return EventList(self._events[fight_id], self)

    # def _fetch_events(self, filter_expression: str='', fight_ids: list[Int]=[]) -> EventList:
    #     start_time = self.first_fight().start_time
    #     all_events = []
    #     while start_time:
    #         res = self._client.q(Q_EVENTS, params={
    #             'reportCode': self.code,
    #             'encounterID': self.encounter.value,
    #             'startTime': start_time,
    #             'endTime': self.last_fight().end_time,
    #             'filter': filter_expression,
    #             'fightIDs': fight_ids})
    #         events = res['reportData']['report']['events']
    #         all_events += [*map(Event, events['data'])]
    #         start_time = events['nextPageTimestamp']

    #     return EventList(all_events, self)

    # def filter(self, filter_str: str, fight_id: int=None) -> EventList:
    #     if fight_id:
    #         return self._fetch_events(filter_str, [fight_id])
    #     else:
    #         return self._fetch_events(filter_str)

    # def deaths(self, fight_id: int) -> EventList:
    #     return self._fetch_events("inCategory('deaths') = true", [fight_id])

    # def casts(self, ability_name: str, *args) -> EventList:
    #     filter_str = f'type="cast" AND ability.name="{ability_name}"'
    #     return self.filter(filter_str, *args)

    # def actions(self, ability_name: str, *args) -> EventList:
    #     filter_str = f'ability.name="{ability_name}"'
    #     return self.filter(filter_str, *args)

    # def dummy_downs(self) -> EventList:
    #     return self._fetch_events("type='applydebuff' AND target.disposition='friendly' AND ability.name='Damage Down'")

    def links(self, events: EventList, offset: int=0, separator: str='\n') -> None:
        ls = list()
        for event in events:
            phase = self.pm.phase_name(event)
            time = self._relative_time(event.time + offset)
            phase_time = self.pm.phase_time(event) / 1000 # in seconds
            ls.append(f'{self._to_output(time)} {event.fight}{phase}@{phase_time:.0f}s')
        print(separator.join(ls))

    def print_pull_times(self) -> Report:
        """Print start time for all fights"""
        for fight in self._fights.values():
            time = self._relative_time(fight.start_time)
            phase = self.pm._to_phase_name(fight.last_phase)
            output = f'{self._to_output(time)} Start of F{fight.i}-end:{phase}{fight.percent}%'
            print(output)
        return self

    def print_phase_times(self, phases: list[str], offset=0) -> Report:
        """Takes a list of phase names and outputs the start of those phases"""
        for phase_event in self.pm.phase_starts(phases):
            phase = self.pm.phase_name(phase_event)
            time = self._relative_time(phase_event.time + offset)
            fight_id = phase_event.fight

            output = f'{self._to_output(time)} '
            output += f'Fight{fight_id}:{100 - self.fight(fight_id).percent:.2f}%:{phase}'
            print(output)
        return self

    # outputs:
    def set_video_offset_time(self, mmss: str, fight_id: int) -> Report:
        """Put in timestamp of video at Fight fight_id"""
        minutes, seconds = mmss.split(':')
        ms = int(minutes)*1000*60 + int(seconds)*1000

        fight = self.fight(fight_id)
        self.offset = ms - fight.start_time
        return self

    def _relative_time(self, time: int) -> tuple(int, int, int):
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
        if self.output_type is None:
            raise ValueError('No output type selected.')

        match self.output_type:
            case Platform.YOUTUBE:
                return self._youtube_time(time)
            case Platform.TWITCH:
                if self.output_code is None:
                    raise ValueError('No twitch video code.')
                return self._twitch_url(time, self.output_code)
            case _:
                raise ValueError('Not a supported platform')

