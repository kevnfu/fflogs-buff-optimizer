from __future__ import annotations
from typing import Any

import itertools 
import json

from enums import Encounter
from data import Event, EventList, Fight

Q_TIMELINE = """
query Timeline ($reportCode: String!, $encounterID: Int!, $startTime: Float, $endTime: Float){
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            deaths: events(dataType: Deaths, hostilityType: Enemies, limit: 10000,
                encounterID: $encounterID,
                startTime: $startTime, endTime: $endTime) {
                data
                # nextPageTimestamp
            }
            targetable: events(hostilityType: Enemies, limit: 10000,
                encounterID: $encounterID,
                filterExpression: "type='targetabilityupdate'",
                startTime: $startTime, endTime: $endTime) {
                data
                # nextPageTimestamp
            }
        }
    }
}
"""


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

    def _build(self, fight_id: int) -> EventList:
        """Creates timeline for one fight"""
        raise NotImplementedError('Use subclass of PhaseReport')

    def __init__(self, report: Report) -> None:
        self._report = report

        # override
        self.PHASE_NAMES = None

        # dict[fight_id: timeline], populated by _build()
        self.timelines = dict() 

    def _build_all(self) -> None:
        for fight_id in self._report._fights.keys():
            self.timelines[fight_id] = self._build(fight_id)

    @require_timeline
    def phase(self, event: Event) -> int:
        """Returns the phase number of the event"""
        timeline = self.timelines[event.fight] 
        passed_checkpoints = timeline.before(event)
        return len(passed_checkpoints) - 1

    def phase_name(self, event: Event) -> str:
        return self._to_phase_name(self.phase(event))

    @require_timeline
    def phase_start(self, event: Event) -> Event:
        """Returns the event that marks the start of the phase"""
        timeline = self.timelines[event.fight]
        passed_checkpoints = timeline.before(event)
        return passed_checkpoints[-1]

    def phase_time(self, event: Event) -> int:
        """Returns phase-relative time of event (in ms)"""
        return event.time - self.phase_start(event).time

    def phase_starts(self, phases: str | list[str]) -> EventList:
        """Returns a list of events corresponding to the start of phase_index phases"""
        self._build_all()
        if isinstance(phases, str):
            phases = [phases]

        phase_indexes = [self._to_phase_index(p) for p in phases]

        phase_events = list()
        for timeline in self.timelines.values():
            phase_events += [timeline[i] for i in phase_indexes if i < len(timeline)]
        
        return EventList(phase_events, self._report)

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

        self.PHASE_NAMES = ['P1', 'P2', 'P3', 'P4', 'I', 'P5', 'P6', 'P7']

    def _build(self, fight_id: int) -> EventList:
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
            return EventList(timeline, self._report)

        # Events for this fight is only based on deaths and boss targetables.
        deaths = self._report.events(fight.i).types('death').to_npcs()
        targetable = self._report.events(fight.i).types("targetabilityupdate")\
            .filter(lambda e: e.targetable==True)

        # Join both types of events and order chronologically
        phase_events = (deaths + targetable).sort_time()
        
        # timeline = list()
        # special P1 -> P2 case
        # In phase 1, first event is Adelphel targetable. Third is Charlbert
        if fight.last_phase == 1 and len(phase_events) > 2 and \
            phase_events[0].target != phase_events[2].target:
                # timeline is start of P1, Thordan appearing (4th event)
                timeline = [Event.from_time(fight.start_time, fight.i), phase_events[4]]
        else:
            # Assume started P2
            # p1 start in the undefined past(-1 time), p2 start is fight start
            timeline = [Event.from_time(-1, fight.i), Event.from_time(fight.start_time, fight.i)]
            # then, include events based on the event index.
            timeline += [phase_events[i] for i in EVENT_INDEX if i < len(phase_events)]
        
        return EventList(timeline, self._report)

class PhaseModelTea(PhaseModel):
    def __init__(self, report: Report):
        if encounter is not Encounter.TEA:
            raise TypeError(f'Using TEA model for {encounter=}')
        
        super().__init__(report)
        self.PHASE_NAMES = ['P1', 'I1', 'P2', 'I2', 'P3', 'P4']


    def _build(self, fight_id: int) -> EventList:
        # Cruise chaser casts Hawk Blaster
        # BJ/CC Targetable
        # Both bj/cc untargetable
        # Alex Prime targetable
        # first down for the count fades
        

        fight = self._report.fight(fight_id)

        raise NotImplementedError('Use subclass of PhaseReport')