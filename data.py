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
    etc: Dict[str, Any]

    def __init__(self, data: Dict[str, Any]) -> None:
        self.time = data.pop('timestamp')
        self.type_ = data.pop('type')
        self.source = data.pop('sourceID', -1)
        self.target = data.pop('targetID', -1)
        self.fight = data.pop('fight')
        self.etc = data

    def __str__(self):
        return str(json.dumps(self.to_dict(), indent=2))

    def to_dict(self):
        return {
            'time':self.time, 
            'type': self.type_, 
            'sourceID': self.source,
            'targetID': self.target,
            'fight': self.fight,
            } | self.etc

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

    def type_(self, type_str: str) -> EventList:
        new_list = [e for e in self._ls if e.type_==type_str]
        return EventList(new_list, self._r)

    def types(self, types: list(str)) -> EventList:
        new_list = [e for e in self._ls if e.type_ in types]
        return EventList(new_list, self._r)

    def in_phase(self, phase: str) -> EventList:
        new_list = [e for e in self._ls if self._r.pm.phase_name(e) == phase]
        return EventList(new_list, self._r).order_by_phase_time()

    def in_phases(self, phases: List[str]) -> EventList:
        new_list = [self.pm.in_phase(p) for p in phases]
        return EventList(new_list, self._r)

    def in_fight(self, fight_id: int) -> EventList:
        new_list = [e for e in self._ls if e.fight==fight_id]
        return EventList(new_list, self._r)

    def in_fights(self, fight_ids: List[int]) -> EventList:
        new_list = [e for e in self._ls if e.fight in fight_ids]
        return EventList(new_list, self._r)

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

    def order_by_time(self) -> EventList:
        self._ls.sort(key=lambda i: i.time)
        return self

    def order_by_phase(self) -> EventList:
        self._ls.sort(key=lambda i: self._r.pm.phase(i))
        return self

    def order_by_phase_time(self) -> EventList:
        self._ls.sort(key=lambda i: (self._r.pm.phase_time(i)))
        return self

    def output(self, *args) -> EventList:
        self._r.output_events(self, *args)
        return self

    def named(self) -> EventList:
        for event in self._ls:
            event.source = self._r.actors_by_id[event.source].name
            event.target = self._r.actors_by_id[event.target].name

            if 'abilityGameID' in event.etc:
                event.etc['abilityGameID'] = self._r.abilities_by_id[event.etc['abilityGameID']].name
            if 'extraAbilityGameID' in event.etc:
                event.etc['extraAbilityGameID'] = self._r.abilities_by_id[event.etc['extraAbilityGameID']].name
        return self

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
    # report: Report

    def __init__(self, data: Dict[str, Any]) -> None:
        self.i=data['id']
        self.encounter=data['encounterID']
        self.start_time=data['startTime']
        self.end_time=data['endTime']
        self.percent=data['fightPercentage']
        self.last_phase=data['lastPhaseAsAbsoluteIndex']
        # self.report=report