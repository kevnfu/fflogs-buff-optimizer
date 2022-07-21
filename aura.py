from __future__ import annotations
from typing import Any

import json

from enums import Encounter
from data import Event, EventList

# does not include healing events
Q_AURAS = """
query Auras ($reportCode: String!, $startTime: Float, $endTime: Float, $fightIDs: [Int]) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            auras: events(limit: 10000, dataType: Buffs, # hostilityType: Enemies,
                startTime: $startTime, endTime: $endTime,
                filterExpression: "inCategory('auras')=true AND inCategory('healing')=false AND type in ('applybuff','applydebuff','removebuff','removedebuff')",
                fightIDs: $fightIDs) {
                data
                nextPageTimestamp
            }
        }
    }
}
"""

Q_COMBATANT_INFO = """
query CombatantInfo ($reportCode: String!, $startTime: Float, $endTime: Float, $fightIDs: [Int]) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            info: events(limit: 10000, # hostilityType: Enemies,
                startTime: $startTime, endTime: $endTime,
                filterExpression: "type='combatantinfo'",
                fightIDs: $fightIDs) {
                data
            }
        }
    }
}
"""

Q_HEALING_AURAS = """
query Auras ($reportCode: String!, $startTime: Float, $endTime: Float, $fightIDs: [Int]) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            auras: events(limit: 10000, dataType: Buffs, # hostilityType: Enemies,
                startTime: $startTime, endTime: $endTime,
                filterExpression: "inCategory('auras')=true AND inCategory('healing')=true AND type in ('applybuff','applydebuff','removebuff','removedebuff')",
                fightIDs: $fightIDs) {
                data
                nextPageTimestamp
            }
        }
    }
}
"""

def require_auras(func):
    '''Decorator that gets auras for a fight if needed before the function'''
    def ensured(*args, **kwargs):
        self = args[0]
        event = args[1]
        fight_id = event.fight
        if fight_id not in self.auras:
            fight = self._report.get_fight(fight_id)
            auras = self._fetch_combatant_info(fight) + \
                self._fetch_auras(fight)

            with open('test.json', 'w') as f:
                auras.named().write(f)

            self.auras[fight_id] = reversed(auras)
        return func(*args, **kwargs)
    return ensured

class AuraModel:

    def __init__(self, client: FFClient, report: Report):
        self.code = report.code
        self._report = report
        self._client = client
        self.auras = dict() # fightID: aura mapping

    def _fetch_combatant_info(self, fight: Fight) -> EventList:
        """convert prepull buffs into apply events"""
        res = self._client.q(Q_COMBATANT_INFO, params={
            'reportCode': self.code,
            'startTime': fight.start_time,
            'endTime': fight.end_time,
            'fightIDs': [fight.i]})
        combatant_info = res['reportData']['report']['info']['data']

        apply_events = list()
        for combatant in combatant_info:
            for aura in combatant['auras']:
                apply_events.append(
                    Event({
                    'timestamp': combatant['timestamp'],
                    'type': 'applybuff',
                    'sourceID': combatant['sourceID'],
                    'targetID': combatant['sourceID'],
                    'fight': fight.i,
                    'abilityGameID': aura['ability'],
                    'stacks': aura['stacks'],
                    'duration': fight.end_time-fight.start_time
                }))

        return EventList(apply_events, self._report)

    def _fetch_auras(self, fight: Fight) -> EventList:
        all_events = list()
        start_time = fight.start_time
        while start_time:
            res = self._client.q(Q_AURAS, params={
                'reportCode': self.code,
                'startTime': start_time, 
                'endTime': fight.end_time,
                'fightIDs': [fight.i]})
            events = res['reportData']['report']['auras']
            all_events += [Event(e) for e in events['data']]
            start_time = events['nextPageTimestamp']
        return EventList(all_events, self._report)

    @require_auras
    def all_on_event(self, event: Event) -> EventList:
        """All auras active on all entities at the time of an event, returning the list of apply events"""
        auras = self.auras[event.fight]

        # get all preceding events
        auras = auras.before(event)

        # get the first event (last chronologically) for that target/ability
        seen_auras = set()
        most_recent = list()
        for a in auras:
            if k:=(a.target, a.etc['abilityGameID']) not in seen_auras:
                seen_auras.add(k)
                most_recent.append(a)

        return EventList(reversed(most_recent), self._report)

    def all_on(self, event: Event) -> dict(int, int):
        """All auras active on all entities at the time of an event, returning a targetID:[abilityID] dict"""
        pass

    def aura(self, aura: int, fight_id: int) -> EventList:
        """All occurences of an aura, returning the list of apply events"""
        pass




