from __future__ import annotations

import json
import itertools 
from operator import itemgetter

from dataclasses import dataclass
from math import floor
from enums import Encounter

from queries import Q_REPORT, Q_DEATHS_OVERKILLS, Q_EVENTS, Q_TIMELINE


@dataclass
class Fight:
    """docstring for Fight"""
    i: int
    encounterID: int
    startTime: int
    endTime: int
    percent: float
    lastPhase: int
    # report: Report

    def __init__(self, data: dict) -> None:
        self.i=data['id']
        self.encounterID=data['encounterID']
        self.startTime=data['startTime']
        self.endTime=data['endTime']
        self.percent=data['fightPercentage']
        self.lastPhase=data['lastPhaseAsAbsoluteIndex']

@dataclass
class Event:
    time: int
    etype: str
    source: int
    target: int
    fight: int
    ect: dict

    def __init__(self, data: dict) -> None:
        self.time = data['timestamp']
        self.etype = data['type']
        self.source = data['sourceID']
        self.target = data['targetID']
        self.fight = data['fight']
        del data['timestamp']
        del data['type']
        del data['sourceID']
        del data['targetID']
        del data['fight']
        self.ect = data

    def __str__(self):
        return f'Event(time={self.time})'

    @classmethod
    def from_time(cls, time: int, fight: int=-1) -> Event:
        return cls({
            'timestamp': time,
            'type': 'time',
            'sourceID': -1,
            'targetID': -1,
            'fight': fight
            })

def require_model(func):
    '''Decorator that calls build on the model if needed before the function'''
    def ensured(*args, **kwargs):
        self = args[0]
        if self.timelines is None:
            self.build()
        return func(*args, **kwargs)
    return ensured

class DSU_PHASE_MODEL:
    encounterID = Encounter.DSU
    _PHASE_NAMES = [
        (0, "P1"),
        (1, "P2"),
        (2, "P3"),
        (3, "P4"),
        (4, "I"),
        (5, "P5"),
        (6, "P6"),
        (7, "P7"),
    ]

    def __init__(self, report: Report):
        assert self.encounterID == report.encounterID
        self._report = report
        self._client = report._client
        self.code = report.code
        self.timelines = None

    def build(self):
        """Required to start using the model"""
        res = self._client.q(Q_TIMELINE, {
            'reportCode': self.code, 
            'startTime': self._report.startTime, 
            'endTime': self._report.endTime})
        report = res['reportData']['report']

        targetable = map(Event, report['targetable']['data'])
        deaths = map(Event, report['deaths']['data'])

        # filter for become targetable
        targetable = filter(lambda e: e.ect['targetable']==True, targetable) 

        phase_events = itertools.chain(deaths, targetable)
        phase_events = sorted(phase_events, key=lambda e: e.time)

        timelines = dict() # timeline is a list of events that mark a beginning of a phase
        for fight in self._report.fights:
            # look at events for specific fight
            events = [e for e in phase_events if e.fight==fight.i]
            
            timeline = list()
            if fight.lastPhase == 0: # Adelphel, Grinnaux, and Charlbert
                timeline = [Event.from_time(fight.startTime, fight.i)] # p1 start == fight start

            # special P1 -> P2 case
            elif fight.lastPhase == 1 and len(events) > 2: # King Thordan
                # if phase 1, first event is Adelphel targetable. Third is Charlbert
                if events[0].target != events[2].target: 
                    timeline = [
                        Event.from_time(fight.startTime, fight.i), 
                        events[4]]

            else:
                # Assume started P2
                # p1 start in the undefined past, p2 start == fight start
                timeline = [Event.from_time(-1, fight.i), Event.from_time(fight.startTime, fight.i)]
                event_index = [
                    2, # Thordan Death
                    4, # Nidhogg Death
                    8, # Both eyes dead
                    12, # Thordan targetable
                    16, # Dragons targetable
                    26, # Dragon-King thordan targetable
                ]

                timeline += [events[i] for i in event_index if i < len(events)]
            
            timelines[fight.i] = timeline
        self.timelines = timelines

    def phase(self, event: Event) -> int:
        """Returns the phase index of the event"""
        timeline = self.timelines[event.fight]
        passed_checkpoints = [e for e in timeline if e.time <= event.time]
        return len(passed_checkpoints) - 1

    def phase_start(self, event: Event) -> Event:
        """Returns the event that marks the start of the phase"""
        timeline = self.timelines[event.fight]
        passed_checkpoints = [e for e in timeline if e.time <= event.time]
        return passed_checkpoints[-1]

    def phase_relative(self, event: Event) -> int:
        """Returns phase-relative time of event (in ms)"""
        return event.time - self.phase_start(event).time

    def get_all_phase_starts(self, phase_indexes: list) -> list:
        """Returns a list of events corresponding to the start of phase_index phases"""
        phase_events = list()
        for timeline in self.timelines.values():
            phase_events += [timeline[i] for i in phase_indexes if i < len(timeline)]
        return phase_events


    @classmethod
    def phase_from_index(cls, index: int) -> str:
        return [x[1] for x in cls._PHASE_NAMES if index in x][0]

    @classmethod
    def index_from_phase(cls, phase: str) -> int:
        return [x[0] for x in cls._PHASE_NAMES if phase in x][0]


class Report:
    """Report for one type of encounter"""
    def __init__(self, code: str, client: 'FFClient', encounterID: Encounter) -> None:
        self._client = client
        self.code = code
        self.encounterID = encounterID
        self.fetch_data()

        self._phase_model = DSU_PHASE_MODEL(self)

    def fetch_data(self) -> Report:
        res = self._client.q(Q_REPORT, {
            'reportCode': self.code,
            'encounterID': self.encounterID.value})
        with open('master.json', 'w') as f:
            f.write(json.dumps(res, indent=4))

        report = res['reportData']['report']
        with open('actors.json', 'w') as f:
            f.write(json.dumps(report['masterData']['actors'], indent=4))

        with open('abilites.json', 'w') as f:
            f.write(json.dumps(report['masterData']['abilities'], indent=4))

        # master data
        self.actors = report['masterData']['actors']
        # self.actors_by_id = {actor['id']: actor for actor in self.actors}

        self.abilities = {ability['gameID']: ability['name'] for ability in report['masterData']['abilities']}

        # fight data
        self.fights = [Fight(data) for data in report['fights']]
        # startTime and endTime are relative to the report, not unix time
        self.startTime = self.fights[0].startTime
        self.endTime = self.fights[-1].endTime

        return self

    def set_video_offset_time(self, mmss: str, fightID: int) -> Report:
        minutes, seconds = mmss.split(':')
        ms = int(minutes)*1000*60 + int(seconds)*1000
        fight = next(filter(lambda x: x.i == fightID, self.fights))
        self.offset = ms - fight.startTime
        return self

    def set_output_type(self, output_type: Platform, *args) -> Report:
        self.output_type = output_type
        return self

    def _relative_time(self, time: int) -> tuple(int, int, int):
        # returns video timestamp
        ms = time + self.offset
        hour = floor(ms/(1000*60*60) % 24)
        minute = floor(ms/(1000*60) % 60)
        second = floor(ms/(1000) % 60)
        return hour, minute, second

    def build_phase_model(self) -> Report:
        self._phase_model.build()
        return self

    def phase(self, fightID: int, time: int) -> str:
        return self._phase_model.phase(fightID, time)

    def get_fight(self, fightID) -> Fight:
        return next(filter(lambda x: x.i==fightID, self.fights))

    def all_events(self, fightID):
        fight = self.get_fight(fightID)
        startTime = fight.startTime
        
        total_data = []
        while startTime:
            res = self._client.q(Q_EVENTS, params={
                'reportCode': self.code,
                'startTime': startTime, 
                'endTime': fight.endTime})
            events = res['reportData']['report']['events']
            total_data += [*map(Event, events['data'])]
            startTime = events['nextPageTimestamp']

        with open('test.json', 'w') as f:
            f.write(json.dumps(total_data, indent=4))

    # outputs:

    def print_pull_times(self, code: str=None) -> Report:
        """Print start time for all fights"""
        for fight in report.fights:
            hour, minute, second = self._relative_time(fight.startTime)
            if code is None:
                print(f'{hour:02.0f}:{minute:02.0f}:{second:02.0f} Pull {fight.i} Phase {fight.lastPhase}')
            else:
                minute += hour * 60
                print(f'https://www.twitch.tv/videos/{code}?t={minute}m{second}s Pull {fight.i} Phase {fight.lastPhase}')
        return self

    def print_phase_times(self, phases: list, code: str=None) -> Report:
        """Takes a list of phase names and outputs the start of those phases"""
        phase_indexes = [self._phase_model.index_from_phase(p) for p in phases]

        for phase_event in self._phase_model.get_all_phase_starts(phase_indexes):
            phase_index = self._phase_model.phase(phase_event)
            phase = self._phase_model.phase_from_index(phase_index)
            hour, minute, second = self._relative_time(phase_event.time)
            if code is None:
                print(f'{hour:02.0f}:{minute:02.0f}:{second:02.0f} Pull {phase_event.fight} {phase}')
            else:
                minute += hour * 60
                print(f'https://www.twitch.tv/videos/{code}?t={minute}m{second}s Pull {phase_event.fight} Phase {phase}')
        return self