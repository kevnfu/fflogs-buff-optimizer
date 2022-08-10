from __future__ import annotations
from typing import Any

# standard
import json
from math import floor

# custom
from report.enums import Encounter, Platform
from report.queries import Q_MASTER_DATA, Q_FIGHTS, Q_EVENTS, Q_ABILITIES
from report.data import Event, EventList, Fight, Ability, Actor
from report.modules.phases import PhaseModelDsu, PhaseModelTea
from report.modules.aura import AuraModel

class Report:
    """Report for one type of encounter"""
    def __init__(self, code: str, client: 'FFClient', encounter: Encounter) -> None:
        self._client = client
        self.code = code
        self._load_phase_model(encounter)

        self.am = AuraModel(self)
        self.data = dict() # to be filled w/ individual calls

        self._fetch_master_data()
        self._fights = self._fetch_all_fights() # {fight id: fight}
        self._events = dict() # {fight id: EventList w/ all events}

    def _load_phase_model(self, encounter: Encounter):
        self.encounter = encounter
        match self.encounter:
            case Encounter.DSU:
                self.pm = PhaseModelDsu(self)
            case Encounter.TEA:
                self.pm = PhaseModelTea(self)
            case _:
                raise NotImplementedError(f'No phase model for {self.encounter}')

    def _fetch_master_data(self) -> None:
        res = self._client.q(Q_MASTER_DATA, {
            'reportCode': self.code})
        report = res['reportData']['report']
        self.title = report['title']
        self.owner = report['owner']
        self.guild = report['guild']
        self.start_time = report['startTime']
        self.end_time = report['endTime']

        # with open('master.json', 'w') as f:
        #     f.write(json.dumps(res, indent=4))
        # with open('actors.json', 'w') as f:
        #     f.write(json.dumps(report['masterData']['actors'], indent=4))
        # with open('abilites.json', 'w') as f:
        #     f.write(json.dumps(report['masterData']['abilities'], indent=4))

        self.actors = [Actor(a) for a in report['masterData']['actors']]
        self.abilities = [Ability(a) for a in report['masterData']['abilities']]

    def _fetch_all_fights(self) -> list(Fight):
        res = self._client.q(Q_FIGHTS, {
            'reportCode': self.code,
            'encounterID': self.encounter.value}, cache=False)
        report = res['reportData']['report']
        report['fights']
        return {f['id']: Fight(f) for f in report['fights']}

    def _fetch_fight(self, fight_id: int) -> Fight:
        """Tries to obtain fight from the server. Ignores cache"""
        res = self._client.q(Q_FIGHTS, {
            'reportCode': self.code,
            'encounterID': self.encounter.value,
            'fightIDs': [fight_id]}, cache=False)
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

    def _fetch_all_events_all_fights(self) -> None:
        for fight_id in self._fights.keys():
            if fight_id not in self._events:
                self._events[fight_id] = self._fetch_all_events(fight_id)

    def events(self, fight_id: int=None) -> EventList:
        # get all events in report if no fight_id specified
        if fight_id is None:
            self._fetch_all_events_all_fights()
            ret = EventList(list(), self)
            for event_list in self._events.values():
                ret += event_list
            return ret

        # if not a valid fight in the report
        if self.fight(fight_id) is None:
            return None

        # if not yet populated
        if fight_id not in self._events:
            self._events[fight_id] = self._fetch_all_events(fight_id)
        
        # return stored
        return self._events[fight_id]

    def _fetch_events(self, filter_expression: str='', fight_ids: int|list[Int]=[]) -> EventList:
        if isinstance(fight_ids, int):
            fight_ids = [fight_ids]

        start_time = self.first_fight().start_time
        all_events = []
        while start_time:
            res = self._client.q(Q_EVENTS, params={
                'reportCode': self.code,
                'encounterID': self.encounter.value,
                'startTime': start_time,
                'endTime': self.last_fight().end_time,
                'filter': filter_expression,
                'fightIDs': fight_ids})
            events = res['reportData']['report']['events']
            all_events += [*map(Event, events['data'])]
            start_time = events['nextPageTimestamp']

        return EventList(all_events, self)

    def filter(self, filter_str: str, *args) -> EventList:
        return self._fetch_events(filter_str, *args)

    def deaths(self, *args) -> EventList:
        return self.filter("inCategory('deaths') = true", *args)

    def casts(self, ability_name: str, *args) -> EventList:
        filter_str = f'type="cast" AND ability.name="{ability_name}"'
        return self.filter(filter_str, *args)

    def types(self, type_name: str, *args) -> EventList:
        filter_str = f'type="{type_name}"'
        return self.filter(filter_str, *args)

    def abilities(self, ability_name: str, *args) -> EventList:
        filter_str = f'ability.name="{ability_name}"'
        return self.filter(filter_str, *args)

    def dummy_downs(self) -> EventList:
        return self._fetch_events("type='applydebuff' AND target.disposition='friendly' AND ability.name='Damage Down'")

    def print_pull_times(self, *, offset: int=0) -> Report:
        """Print start time for all fights"""
        for fight in self._fights.values():
            time = self._relative_time(fight.start_time + offset)
            phase = self.pm._to_phase_name(fight.last_phase)
            output = f'{self._to_output(time)} Start of F{fight.i}-end:{phase}{fight.percent}%'
            print(output)
        return self

    def print_phase_times(self, phases: str | list[str], *, offset: int=0) -> Report:
        """Takes a list of phase names and outputs the start of those phases"""
        if isinstance(phases, str):
            phases = [phases]

        for phase_event in self.pm.phase_starts(phases):
            phase = self.pm.phase_name(phase_event)
            time = self._relative_time(phase_event.time + offset)
            fight_id = phase_event.fight

            output = f'{self._to_output(time)} '
            output += f'Fight{fight_id}:{100 - self.fight(fight_id).percent:.2f}%:{phase}'
            print(output)
        return self

    # outputs:
    def set_video_offset(self, mmss: str, fight_id: int) -> Report:
        """Put in timestamp of video at Fight fight_id"""
        minutes, seconds = mmss.split(':')
        ms = int(minutes)*1000*60 + int(seconds)*1000

        fight = self.fight(fight_id)
        self.offset = ms - fight.start_time
        return self

    def set_output_type(self, output_type: Platform, code: str=None) -> Report:
        self.output_type = output_type
        self.output_code = code
        return self

    def set_vod(self, vod: Vod) -> Report:
        self.set_video_offset(vod.offset, vod.fight_id)
        self.set_output_type(vod.platform, vod.url)
        return self
        
    def _relative_time(self, time: int) -> tuple[int, int, int]:
        """Takes event time and outputs video time"""
        ms = time + self.offset
        hour = floor(ms/(1000*60*60) % 24)
        minute = floor(ms/(1000*60) % 60)
        second = floor(ms/(1000) % 60)
        return hour, minute, second

    @staticmethod
    def _youtube_time(time: tuple[int, int, int]) -> str:
        hour, minute, second = time
        output_str = ''
        if hour != 0:
            output_str += f'{hour:02.0f}:'
        output_str += f'{minute:02.0f}:{second:02.0f}'
        return output_str

    @staticmethod
    def _youtube_url(time: tuple[int, int, int], code: str) -> str:
        hour, minute, second = time
        second += minute * 60 + hour * 60 * 60
        return f'https://youtu.be/{code}?t={second}'

    @staticmethod
    def _twitch_url(time: tuple[int, int, int], code: str) -> str:
        hour, minute, second = time
        minute += hour * 60
        return f'https://www.twitch.tv/videos/{code}?t={minute}m{second}s'


    def _to_output(self, time: int) -> str:
        if self.output_type is None:
            raise ValueError('No output type selected.')

        match self.output_type:
            case Platform.YOUTUBE:
                return self._youtube_time(time)
            case Platform.YOUTUBE_LINK:
                if self.output_code is None:
                    raise ValueError('No youtube video code.')
                return self._youtube_url(time, self.output_code)
            case Platform.TWITCH:
                if self.output_code is None:
                    raise ValueError('No twitch video code.')
                return self._twitch_url(time, self.output_code)
            case _:
                raise ValueError('Not a supported platform')



def update_ability_list(client: FFClient):
    has_more_pages = True
    page = 1
    abilities = []
    while has_more_pages:
        res = client.q(Q_ABILITIES, {
            'page': page
            })
        res = res['gameData']['abilities']
        page = res['current_page'] + 1
        has_more_pages = res['has_more_pages']
        abilities += res['data']

    with open('ability_master_list.json', 'w') as f:
        json.dump(abilities, f)