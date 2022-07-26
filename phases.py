from __future__ import annotations
from typing import Any

import itertools 
import json

from enums import Encounter
from queries import Q_FIGHTS, Q_TIMELINE
from data import Event, Fight

def require_timeline(func):
    '''Decorator that calls build on the model if needed before the function'''
    def ensured(*args, **kwargs):
        self = args[0]
        event = args[1]
        fight_id = event.fight
        if fight_id not in self.timelines:
            self.timelines[fight_id] = self._build(fight_id)

        return func(*args, **kwargs)
    return ensured

class PhaseModel:
    """
    Returns phase information about an event. Builds a timeline of events for a report.
    By searching for particular kinds of events, a fight will produce a predictable series of events.
    A timeline is a list of events, or checkpoints, that mark the progression of a fight.
    The first event is the start of the first phase, the second event is the start of the second, etc.
    """

    def _build(self, fight_id: int) -> list[Event]:
        """Creates timeline for one fight"""
        raise NotImplementedError('Use subclass of PhaseReport')

    def __init__(self, report: Report) -> None:
        self.code = report.code
        self._report = report
        self.encounter = report.encounter
        self._client = report._client

        # override
        self.PHASE_NAMES = None

        # dict[fight_id: timeline], populated by _build()
        self.timelines = dict() 


    def _fetch_timeline_events(self, fight: Fight) -> dict[str, Any]:
        """Returns response from server containing timeline events"""
        res = self._client.q(Q_TIMELINE, {
            'reportCode': self.code,
            'encounterID': self.encounter.value,
            'startTime': fight.start_time, 
            'endTime': fight.end_time})
        return res

    def _build_all(self) -> None:
        for fight_id in self._report._fights.keys():
            self.timelines[fight_id] = self._build(fight_id)

    @require_timeline
    def phase(self, event: Event) -> int:
        """Returns the phase number of the event"""
        timeline = self.timelines[event.fight] 
        passed_checkpoints = [e for e in timeline if e.time <= event.time]
        return len(passed_checkpoints) - 1

    def phase_name(self, event: Event) -> str:
        return self._to_phase_name(self.phase(event))

    @require_timeline
    def phase_start(self, event: Event) -> Event:
        """Returns the event that marks the start of the phase"""
        timeline = self.timelines[event.fight]
        passed_checkpoints = [e for e in timeline if e.time <= event.time]
        return passed_checkpoints[-1]

    def phase_time(self, event: Event) -> int:
        """Returns phase-relative time of event (in ms)"""
        return event.time - self.phase_start(event).time

    def phase_starts(self, phases: list[str]) -> list[Event]:
        """Returns a list of events corresponding to the start of phase_index phases"""
        self._build_all()
        phase_indexes = [self._to_phase_index(p) for p in phases]

        phase_events = list()
        for timeline in self.timelines.values():
            phase_events += [timeline[i] for i in phase_indexes if i < len(timeline)]
        
        return phase_events

    def valid_phase(self, phase: str) -> bool:
        return phase in self.PHASE_NAMES

    def _to_phase_name(self, index: int) -> str:
        return self.PHASE_NAMES[index]

    def _to_phase_index(self, phase: str) -> int:
        return self.PHASE_NAMES.index(phase)


class PhaseModelDsu(PhaseModel):
    def __init__(self, report: Report):
        if report.encounter is not Encounter.DSU:
            raise TypeError(f'Using DSU model for {encounter=}')

        super().__init__(report)

        self.PHASE_NAMES = ["P1", "P2", "P3", "P4", "I", "P5", "P6", "P7"]

    def _build(self, fight_id: int) -> list[Event]:
        EVENT_INDEX = [
            2, # Thordan Death
            4, # Nidhogg Death
            8, # Both eyes dead
            12, # Thordan targetable
            16, # Dragons targetable
            26,] # Dragon-King thordan targetable

        fight = self._report.fight(fight_id)

        # special case fight ended phase 1; timeline is a single event: fight start
        if fight.last_phase == 0: # Fight ended phase 1
            timeline = [Event.from_time(fight.start_time, fight.i)] # p1 start == fight start
            return timeline

        res = self._fetch_timeline_events(fight)
        report = res['reportData']['report']

        # Events for this fight is only based on deaths and boss targetables.
        targetable = map(Event, report['targetable']['data'])
        targetable = filter(lambda e: e.targetable==True, targetable)
        deaths = map(Event, report['deaths']['data'])

        # Join both types of events and order chronologically
        phase_events = itertools.chain(deaths, targetable)
        phase_events = sorted(phase_events, key=lambda e: e.time)

        # special P1 -> P2 case
        if fight.last_phase == 1 and len(phase_events) > 2:
            # In phase 1, first event is Adelphel targetable. Third is Charlbert
            if phase_events[0].target != phase_events[2].target: 
                # timeline is start of P1, Thordan appearing (4th event)
                timeline = [Event.from_time(fight.start_time, fight.i), phase_events[4]]
        else:
            # Assume started P2
            # p1 start in the undefined past(-1 time), p2 start is fight start
            timeline = [Event.from_time(-1, fight.i), Event.from_time(fight.start_time, fight.i)]
            # then, include events based on the event index.
            timeline += [phase_events[i] for i in EVENT_INDEX if i < len(phase_events)]
        
        return timeline

class PhaseModelTea(PhaseModel):
    def __init__(self, code: str, client: FFClient, encounter: Encounter):
        super().__init__(code, client, encounter)

        if encounter is not Encounter.TEA:
            raise TypeError(f'Using TEA model for {encounter=}')

    def build(self):
        raise NotImplementedError