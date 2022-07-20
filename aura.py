from __future__ import annotations
from typing import Any

import json

from enums import Encounter
from data import Event

Q_AURAS = """
query Auras ($reportCode: String!, $startTime: Float, $endTime: Float, $filter: String, $fightIDs: [Int]) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            buffs: events(limit: 10000, dataType: Buffs
                startTime: $startTime, endTime: $endTime,
                filterExpression: $filter,
                fightIDs: $fightIDs) {
                data
                nextPageTimestamp
            }
            debuffs: events(limit: 10000, dataType: Debuffs
                startTime: $startTime, endTime: $endTime,
                filterExpression: $filter,
                fightIDs: $fightIDs) {
                data
                nextPageTimestamp
            }
        }
    }
}
"""

class AuraModel:

    def __init__(self, code: str, client: FFClient, report: Report):
        self.code = code
        self._report = report
        self._client = client

    def test(self):
        fight = self._report.get_fight(1)

        res = self._client.q(Q_AURAS, {
            'reportCode': self.code,
            'startTime': fight.start_time,
            'endTime': fight.end_time,})
        report = res['reportData']['report']
        buffs = [Event(e) for e in report['buffs']['data']]
        debuffs = [Event(e) for e in report['debuffs']['data']]

        with open('test.json', 'w') as f:
            for buff in buffs:
                f.write(str(buff) + '\n')




