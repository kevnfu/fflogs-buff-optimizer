from __future__ import annotations
from typing import List, Dict, Tuple, Iterator, Any

import json

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
        d = {
            'time':self.time, 
            'type': self.type_, 
            'sourceID': self.source,
            'targetID': self.target,
            'fight': self.fight,
            } | self.etc
        return str(json.dumps(d, indent=2))

    @classmethod
    def from_time(cls, time: int, fight: int=-1) -> Event:
        return cls({
            'timestamp': time,
            'type': 'time',
            'sourceID': -1,
            'targetID': -1,
            'fight': fight
            })


class EventList:
    """Wrapper around a list of events. Contains reference to report"""
    def __init__(self, ls: List[Event], report: Report) -> None:
        self._r = report
        self._ls = ls

    def __add__(self, other: EventList) -> EventList:
        assert self._r is other._r
        return EventList(self._ls + other._ls, self._r)

    def to_list(self) -> List:
        return self._ls

    def in_phase(self, phase: str) -> EventList:
        new_list = [e for e in self._ls if self._r.phase_name(e) == phase]
        return EventList(new_list, self._r).order_by_phase_time()

    def in_phases(self, phases: List[str]) -> EventList:
        new_list = EventList(list(), self._r)
        for p in phases:
            new_list += self.in_phase(p)
        return new_list

    def in_fight(self, fightID: int) -> EventList:
        pass

    def by(self, name: str) -> EventList:
        actor_ids = self._r.get_actor_ids(name)
        print(actor_ids)
        new_list = [e for e in self._ls if e.source in actor_ids]
        return EventList(new_list, self._r)

    def to(self, name: str) -> EventList:
        actor_ids = self._r.get_actor_ids(name)
        new_list = [e for e in self._ls if e.target in actor_ids]
        return EventList(new_list, self._r)

    def order_by_time(self) -> EventList:
        self._ls.sort(key=lambda i: i.time)
        return self

    def order_by_phase(self) -> EventList:
        self._ls.sort(key=lambda i: self._r.phase(i))
        return self

    def order_by_phase_time(self) -> EventList:
        self._ls.sort(key=lambda i: (self._r.phase_time(i)))
        return self

    def __iter__(self):
        return self._ls.__iter__()

    def __next__(self):
        self._ls.__next__()

    def __repr__(self):
        return self._ls.__repr__()

    def __len__(self):
        return self._ls.__len__()
