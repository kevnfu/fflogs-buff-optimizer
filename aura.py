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

class AuraModel:

    def __init__(self, client: FFClient, report: Report):
        self.code = report.code
        self._report = report
        self._client = client

    def _fetch_auras(self, fight: Fight) -> EventList:
        all_events = []
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

    def test(self):
        fight = self._report.get_fight(25)
        auras = self._fetch_auras(fight)
        print(len(auras))

        with open('test.json', 'w') as f:
            auras.named().write(f)
        

    def all_on(self, target: int, time: int) -> list(Event):
        """All auras on one person at a specific time, returning the list of apply events"""
        pass

    def aura(self, aura: int) -> list(Event):
        """All occurences of an aura, returning the list of apply events"""
        pass




