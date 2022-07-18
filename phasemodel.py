from __future__ import annotations
from typing import List, Dict, Tuple, Iterator, Any

import itertools 

from enums import Encounter
from queries import Q_TIMELINE
from events import Event

def require_model(func):
    '''Decorator that calls build on the model if needed before the function'''
    def ensured(*args, **kwargs):
        self = args[0]
        if self.timelines is None:
            self.build()
        return func(*args, **kwargs)
    return ensured

class PhaseModelUser:
    def __init__(self, model: PhaseModel):
        self._model = model

    # phase model methods
    def phase(self, event: Event) -> int:
        """Returns the phase index of the event"""
        return self._model.phase(event)

    def phase_name(self, event: Event) -> str:
        """Returns the phase name of the event"""
        return self._model.phase_name(event)

    def phase_time(self, event: Event) -> int:
        return self._model.phase_time(event)

    def get_phase_starts(self, phases: List[str]) -> List[Event]:
        """Returns a list of events corresponding to the start of phase_index phases"""
        return self._model.get_phase_starts(phases)

class PhaseModel:
    # override
    _PHASE_NAMES = None
    EVENT_INDEX = None
    ENCOUNTER = None

    def build(self):
        pass

    def __init__(self, code: str, client: FFClient, fights: List[Fight]) -> None:
        self.code = code
        self._client = client
        self.fights = fights
        self.timelines = None

    def _fetch_timeline_events(self) -> Dict[str, Any]:
        """Returns response from server containing timeline events"""
        res = self._client.q(Q_TIMELINE, {
            'reportCode': self.code, 
            'encounterID': self.ENCOUNTER.value,
            'startTime': self.fights[0].start_time, 
            'endTime': self.fights[-1].end_time})
        return res

    @require_model
    def phase(self, event: Event) -> int:
        """Returns the phase index of the event"""
        timeline = self.timelines[event.fight]
        passed_checkpoints = [e for e in timeline if e.time <= event.time]
        return len(passed_checkpoints) - 1

    def phase_name(self, event: Event) -> int:
        return self.phase_from_index(self.phase(event))

    @require_model
    def phase_start(self, event: Event) -> Event:
        """Returns the event that marks the start of the phase"""
        timeline = self.timelines[event.fight]
        passed_checkpoints = [e for e in timeline if e.time <= event.time]
        return passed_checkpoints[-1]

    def phase_time(self, event: Event) -> int:
        """Returns phase-relative time of event (in ms)"""
        return event.time - self.phase_start(event).time

    @require_model
    def get_phase_starts(self, phases: List[str]) -> List[Event]:
        """Returns a list of events corresponding to the start of phase_index phases"""
        phase_indexes = [self.index_from_phase(p) for p in phases]
        phase_events = list()
        for timeline in self.timelines.values():
            phase_events += [timeline[i] for i in phase_indexes if i < len(timeline)]
        return phase_events

    @require_model
    def get_fight_timeline(self, fight_id: int) -> List[Event]:
        return self.timelines[fight_id]

    @classmethod
    def phase_from_index(cls, index: int) -> str:
        return [x[1] for x in cls._PHASE_NAMES if index in x][0]

    @classmethod
    def index_from_phase(cls, phase: str) -> int:
        return [x[0] for x in cls._PHASE_NAMES if phase in x][0]


class PhaseModelDsu(PhaseModel):
    _PHASE_NAMES = [
        (0, "P1"),
        (1, "P2"),
        (2, "P3"),
        (3, "P4"),
        (4, "I"),
        (5, "P5"),
        (6, "P6"),
        (7, "P7"),]

    EVENT_INDEX = [
        2, # Thordan Death
        4, # Nidhogg Death
        8, # Both eyes dead
        12, # Thordan targetable
        16, # Dragons targetable
        26,] # Dragon-King thordan targetable
    
    ENCOUNTER = Encounter.DSU

    def build(self):
        """Required to start using the model"""
        res = self._fetch_timeline_events()
        report = res['reportData']['report']

        targetable = map(Event, report['targetable']['data'])
        deaths = map(Event, report['deaths']['data'])

        # filter for become targetable
        targetable = filter(lambda e: e.etc['targetable']==True, targetable) 

        phase_events = itertools.chain(deaths, targetable)
        phase_events = sorted(phase_events, key=lambda e: e.time)

        timelines = dict() # timeline is a list of events that mark a beginning of a phase
        for fight in self.fights:
            # look at events for specific fight
            events = [e for e in phase_events if e.fight==fight.i]
            
            timeline = list()
            if fight.lastPhase == 0: # Adelphel, Grinnaux, and Charlbert
                timeline = [Event.from_time(fight.start_time, fight.i)] # p1 start == fight start

            # special P1 -> P2 case
            elif fight.lastPhase == 1 and len(events) > 2: # King Thordan
                # if phase 1, first event is Adelphel targetable. Third is Charlbert
                if events[0].target != events[2].target: 
                    timeline = [
                        Event.from_time(fight.start_time, fight.i), 
                        events[4]]

            else:
                # Assume started P2
                # p1 start in the undefined past, p2 start == fight start
                timeline = [Event.from_time(-1, fight.i), Event.from_time(fight.start_time, fight.i)]
                timeline += [events[i] for i in self.EVENT_INDEX if i < len(events)]
            
            timelines[fight.i] = timeline
        self.timelines = timelines