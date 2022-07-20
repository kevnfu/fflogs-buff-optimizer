from __future__ import annotations
from typing import List, Dict, Tuple, Iterator, Any

from enums import Encounter

Q_AURAS = """
query Auras ($reportCode: String!, $startTime: Float, $endTime: Float, $filter: String, $fightIDs: [Int]) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            buffs: events(limit: 10000, dataType="Buffs"
                startTime: $startTime, endTime: $endTime,
                filterExpression: $filter,
                fightIDs: $fightIDs) {
                data
                nextPageTimestamp
            }
            debuffs: events(limit: 10000, dataType="Debuffs"
                startTime: $startTime, endTime: $endTime,
                encounterID: $encounterID,
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

    def _fetch_fight(self, fight_id: int) -> Fight:
        """Fetch one fight from the report"""
        res = self._client.q(Q_FIGHTS, {
            'reportCode': self.code,
            'encounterID': self.encounter.value,
            'fightIDs': [fight_id]})
        return Fight(res['reportData']['report']['fights'][0])

    def test(self):
        res = self._client.q(Q_AURAS, {
            'reportCode': self.code,
            'startTime': start_time,
            'endTime': end_time,})
        report = res['reportData']['report']
        buffs = [Event(e) for e in report['buffs']]
        debuffs = [Event(e) for e in report['debuffs']]

        with open('test.json') as f:
            for buff in buffs:
                f.write(str(buff) + '\n')




