from __future__ import annotations
from typing import List, Dict, Tuple, Iterator, Any

import json
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

    def __add__(self, other: EventList) -> EventList:
        if self._r is not other._r:
            raise ValueError('Attempting to add events from different reports')
        return EventList(self._ls + other._ls, self._r)

    def to_list(self) -> List:
        return self._ls

    def types(self, types: str | list[str]) -> EventList:
        if isinstance(types, str):
            new_list = [e for e in self._ls if e.type_==types]
        elif isinstance(types, list):
            new_list = [e for e in self._ls if e.type_ in types]
        else:
            raise TypeError(f'needs str or list[str], got {types=}')
        return EventList(new_list, self._r)

    def in_phases(self, phases: str | list[str]) -> EventList:
        if isinstance(phases, str):
            new_list = [e for e in self._ls if self._r.pm.phase_name(e) == phases]
        elif isinstance(phases, list):
            new_list = [self.pm.in_phase(p) for p in phases]
        else:
            raise TypeError(f'needs str or list[str], got {phases=}')
        return EventList(new_list, self._r).sort_phase_time()

    def in_fights(self, fight_ids: int | list[int]) -> EventList:
        if isinstance(fight_ids, int):
            new_list = [e for e in self._ls if e.fight==fight_ids]
        elif isinstance(fight_ids, list):
            new_list = [e for e in self._ls if e.fight in fight_ids]
        else:
            raise TypeError(f'needs int or list[int], got {fight_ids=}')
        return EventList(new_list, self._r)

    def ability(self, ability_name: str) -> EventList:
        ability_ids = self._r.get_ability(ability_name)
        new_list = filter(lambda x: hasattr(x, 'abilityGameID'), self._ls)
        new_list = [e for e in new_list if e.abilityGameID in ability_ids]
        return EventList(new_list, self._r)

    def casts(self, ability_name: str):
        return self.ability(ability_name).types("cast")

    def by(self, name: str) -> EventList:
        if type(self._ls[0].source) is int:
            actor_ids = self._r.get_actor_ids(name)
            new_list = [e for e in self._ls if e.source in actor_ids]
        else:
            new_list = [e for e in self._ls if e.source is name]
        return EventList(new_list, self._r)

    def to(self, name: str) -> EventList:
        if type(self._ls[0].target) is int:
            actor_ids = self._r.get_actor_ids(name)
            new_list = [e for e in self._ls if e.target in actor_ids]
        else:
            new_list = [e for e in self._ls if e.target is name]
        return EventList(new_list, self._r)

    def before(self, event: Event) -> EventList:
        new_list = [e for e in self._ls if e.time <= event.time]
        return EventList(new_list, self._r)

    def after(self, event: Event) -> EventList:
        new_list = [e for e in self._ls if e.time >= event.time]
        return EventList(new_list, self._r)

    def to_source(self) -> list(int | str):
        return [e.source for e in self._ls]

    def to_target(self) ->list(int | str):
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

    def links(self, *args) -> EventList:
        self._r.links(self, *args)
        return self

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