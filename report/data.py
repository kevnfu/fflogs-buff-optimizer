from __future__ import annotations
from typing import Callable, Any

import json
from math import floor
from dataclasses import dataclass

class Event:
    time: int
    type_: str
    source: int
    target: int
    fight: int

    def __init__(self, data: Dict[str, Any]) -> None:
        self.time = data.pop('timestamp')
        self.type_ = data.pop('type')
        self.source = data.pop('sourceID', -1)
        self.target = data.pop('targetID', -1)
        self.fight = data.pop('fight')
        self.__dict__.update(data) 

    def __str__(self):
        return str(json.dumps(self.to_dict(), indent=2))

    def to_dict(self):
        renamed = ['time', 'type_', 'source', 'target']
        etc = {k:v for k,v in self.__dict__.items() if k not in renamed}

        return {
            'timestamp':self.time,
            'type': self.type_, 
            'sourceID': self.source,
            'targetID': self.target,
            } | etc

    @classmethod
    def from_time(cls, time: int, fight: int=-1) -> Event:
        return cls({
            'timestamp': time,
            'type': 'time',
            'sourceID': -1,
            'targetID': -1,
            'fight': fight})

class EventList:
    """Wrapper around a list of events. Contains reference to report"""
    def __init__(self, ls: List[Event], report: Report) -> None:
        self._r = report
        self._ls = ls

    def to_list(self) -> List:
        return self._ls

    def types(self, types: str | list[str]) -> EventList:
        if isinstance(types, str):
            types = [types]
        new_list = [e for e in self._ls if e.type_ in types]
        return EventList(new_list, self._r)

    def in_phases(self, phases: str | list[str]) -> EventList:
        if isinstance(phases, str):
            phases = [phases]
        new_list = [e for e in self._ls if self._r.pm.phase_name(e) in phases]
        return EventList(new_list, self._r).sort_phase_time()

    def in_fights(self, fight_ids: int | list[int]) -> EventList:
        if isinstance(fight_ids, int):
            fight_ids = [fight_ids]
        new_list = [e for e in self._ls if e.fight in fight_ids]
        return EventList(new_list, self._r)

    def ability(self, ability_name: str | list(str)) -> EventList:
        if isinstance(ability_name, str):
            ability_name = [ability_name]
        
        ability_ids = []
        for a in ability_name:
            ability_ids += self._r.get_ability(a)

        new_list = filter(lambda x: hasattr(x, 'abilityGameID'), self._ls)
        new_list = [e for e in new_list if e.abilityGameID in ability_ids]
        return EventList(new_list, self._r)

    def casts(self, ability_name: str | list(str)):
        return self.ability(ability_name).types("cast")

    def by(self, names: str) -> EventList:
        if len(self)==0:
            return EventList(list(), self._r)
        
        if not isinstance(names, list):
            names = [names]

        all_ids = []
        for name in names:
            actor_ids = self._r.get_actor_ids(name)
            all_ids += actor_ids
        
        new_list = [e for e in self._ls if e.target in all_ids]
        return EventList(new_list, self._r)

    def by_id(self, actor_id: int) -> EventList:
        new_list = [e for e in self._ls if e.source is actor_id]
        return EventList(new_list, self._r)

    def by_players(self) -> EventList:
        new_list = [e for e in self._ls if self._r.get_actor(e.source).type_=='Player']
        return EventList(new_list, self._r)

    def by_npcs(self) -> EventList:
        new_list = [e for e in self._ls if self._r.get_actor(e.source).type_=='NPC']
        return EventList(new_list, self._r)

    def to(self, names: str | list[str]) -> EventList:
        if len(self)==0:
            return EventList(list(), self._r)
        if not isinstance(names, list):
            names = [names]

        all_ids = []
        for name in names:
            actor_ids = self._r.get_actor_ids(name)
            all_ids += actor_ids
        
        new_list = [e for e in self._ls if e.target in all_ids]
        return EventList(new_list, self._r)

    def to_players(self) -> EventList:
        new_list = [e for e in self._ls if self._r.get_actor(e.target).type_=='Player']
        return EventList(new_list, self._r)

    def to_npcs(self) -> EventList:
        new_list = [e for e in self._ls if self._r.get_actor(e.target).type_=='NPC']
        return EventList(new_list, self._r)

    def before(self, event: Event) -> EventList:
        new_list = [e for e in self._ls if e.time <= event.time]
        return EventList(new_list, self._r)

    def after(self, event: Event) -> EventList:
        new_list = [e for e in self._ls if e.time >= event.time]
        return EventList(new_list, self._r)

    def to_sources(self) -> list(int | str):
        return [e.source for e in self._ls]

    def to_targets(self) ->list(int | str):
        return [e.target for e in self._ls]

    def sort_time(self, *, reverse=False) -> EventList:
        self._ls.sort(key=lambda i: i.time, reverse=reverse)
        return self

    def sort_phase(self) -> EventList:
        self._ls.sort(key=lambda i: self._r.pm.phase(i))
        return self

    def sort_phase_time(self) -> EventList:
        self._ls.sort(key=lambda i: (self._r.pm.phase_time(i)))
        return self

    def filter(self, func: Callable) -> EventList:
        new_list = [*filter(func, self._ls)]
        return EventList(new_list, self._r)

    def links(self, offset: int=0) -> list[tuple[str, int, int]]:
        link_ls = list()
        for event in self._ls:
            time = self._r._relative_time(event.time + offset)
            print(self._r._to_output(time))
            link_ls.append((f'{self._r._to_output(time)}', event.fight, event.time))
        return link_ls

    def named(self) -> EventList:
        new_list = list()
        for event in self._ls:
            # create new
            new_event = Event(event.to_dict())
            new_list.append(new_event)

            new_event.source = self._r.get_actor(event.source).name
            new_event.target = self._r.get_actor(event.target).name
            new_event.fighttime = event.time - self._r.fight(event.fight).start_time

            try:
                new_event.abilityGameID = self._r.get_ability(event.abilityGameID)
                new_event.extraAbilityGameID = self._r.get_ability(event.extraAbilityGameID)
            except AttributeError:
                continue

        return EventList(new_list, self._r)

    def print(self) -> EventList:
        for e in self._ls:
            print(str(e))
        return self

    def write(self, f: File) -> EventList:
        for e in self._ls:
            f.write(str(e) + '\n')
        return self

    def timeline(self, offset=0) -> EventList:
        for e in self._ls:
            start_cast = self._to_mmss(e.fighttime + offset)
            line = f'{start_cast}'
            if hasattr(e, 'duration'):
                end_cast = self._to_mmss(e.fighttime + e.duration + offset)
                line += f'\t{end_cast}'
            else:
                line = '\t' + line
            line += f'\t{e.abilityGameID}'
            print(line)

    @staticmethod
    def _to_mmss(ms: int) -> int:
        second = round(ms/(1000) % 60)
        minute = floor(ms/(1000*60) % 60)
        remainder = ms/1000 % 1
        remainder = f'{remainder:.2f}'.lstrip('0')
        out = ''
        if minute != 0:
            out += f'{minute}:'
        out += f'{second:02d}'
        
        return out


    def __str__(self):
        return '\n'.join([str(e) for e in self._ls])

    def __iter__(self):
        return self._ls.__iter__()

    def __next__(self):
        self._ls.__next__()

    def __repr__(self):
        return self._ls.__repr__()

    def __len__(self):
        return self._ls.__len__()

    def __reversed__(self):
        self._ls = list(reversed(self._ls))
        return self 

    def __getitem__(self, index):
        if isinstance(index, slice):
            return EventList(self._ls[index], self._r)
        else:
            return self._ls.__getitem__(index)

    def __setitem__(self, index, data):
        self._ls.__setitem__(index, data)

    def __add__(self, other: EventList) -> EventList:
        if self._r is not other._r:
            raise ValueError('Attempting to add events from different reports')
        return EventList(self._ls + other._ls, self._r)

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
    last_phase: int
    players: list[int]

    def __init__(self, data: Dict[str, Any]) -> None:
        self.i=data['id']
        self.encounter=data['encounterID']
        self.start_time=data['startTime']
        self.end_time=data['endTime']
        self.percent=data['fightPercentage']
        self.last_phase=data['lastPhaseAsAbsoluteIndex']
        self.players=data['friendlyPlayers']

    def __str__(self):
        return str(json.dumps(self.to_dict(), indent=2))

    def to_dict(self):
        return {
            'id': self.i,
            'encounter': self.encounter,
            'startTime': self.start_time,
            'endTime': self.end_time,
            'fightPercentage': self.percent,
            'lastPhaseAsAbsoluteIndex': self.last_phase,
            'friendlyPlayers': self.players}