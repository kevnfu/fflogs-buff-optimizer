from __future__ import annotations
from typing import Any

import json

from report.enums import Encounter
from report.data import Event, EventList

# does not include healing events
Q_AURAS = """
query Auras ($reportCode: String!, $startTime: Float, $endTime: Float, $fightIDs: [Int]) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            auras: events(limit: 10000, # hostilityType: Enemies,
                startTime: $startTime, endTime: $endTime,
                filterExpression: "inCategory('auras')=true AND type in ('applybuff','applydebuff','removebuff','removedebuff')",
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

def require_auras(func):
    '''Decorator that gets auras for a fight if needed before the function'''
    def ensured(*args, **kwargs):
        self = args[0]
        event = args[1]
        fight_id = event.fight
        if fight_id not in self.auras:
            fight = self._report.fight(fight_id)
            auras = self._fetch_combatant_info(fight) + \
                self._fetch_auras(fight)

            # with open('test.json', 'w') as f:
            #     auras.named().write(f)

            self.auras[fight_id] = reversed(auras)
        return func(*args, **kwargs)
    return ensured

class AuraModel:
    """Outputs active buffs/debuffs"""
    def __init__(self, report: Report):
        self.code = report.code
        self._report = report
        self.auras = dict() # fightID: aura mapping
        self.APPLIES = ['applybuff','applydebuff']

    def _fetch_combatant_info(self, fight: Fight) -> EventList:
        """convert prepull buffs into apply events"""
        combatant_info = self._report.events(fight.i).types("combatantinfo")
        apply_events = list()
        for combatant in combatant_info:
            for aura in combatant.auras:
                apply_events.append(
                    Event({
                    'timestamp': combatant.time,
                    'type': 'applybuff',
                    'sourceID': combatant.source,
                    'targetID': combatant.source,
                    'fight': fight.i,
                    'abilityGameID': aura['ability'],
                    'stacks': aura['stacks'],
                    'duration': fight.end_time-fight.start_time
                }))
        return EventList(apply_events, self._report)

    def _fetch_auras(self, fight: Fight) -> EventList:
        return self._report.events(fight.i).types([
            'applybuff','applydebuff','removebuff','removedebuff'])

    @require_auras
    def applied_at(self, event: Event) -> EventList:
        """All auras active on all entities at the time of an event, returning the list of apply events"""
        auras = self.auras[event.fight] # auras is in reversed chronological order

        # get all preceding events
        auras = auras.before(event)

        # get the first event (last chronologically) for that target/ability
        seen_auras = set()
        most_recent = list()
        for a in auras:
            if (k:=(a.target, a.abilityGameID)) not in seen_auras:
                seen_auras.add(k)
                most_recent.append(a)

        # only apply events
        
        most_recent = [e for e in most_recent if e.type_ in self.APPLIES]
        return EventList(list(reversed(most_recent)), self._report)

    def active_at(self, event: Event, *, named=False) -> dict(int, list[int]) | dict(str, list[str]):
        """All auras active on all entities at the time of an event, returning an actor.id:list[ability.id] dict"""
        ret = dict()
        r = self._report
        for e in self.applied_at(event):
            if named is False:
                ret.setdefault(e.target, list()).append(e.abilityGameID)
            else:
                ret.setdefault(r.get_actor(e.target).name, list()).append(r.get_ability(e.abilityGameID))

        return ret

    def aura(self, aura_list: str|int|list[int|str], fight_id: int) -> EventList:
        """All occurences of an aura, returning the list of apply events"""
        # make it a list
        if not isinstance(aura_list, list):
            aura_list = [aura_list]

        # return empty list if no input
        if len(aura_list) == 0:
            return EventList(list(), self._report)

        # convert auras to a list of ability ids
        if isinstance(aura_list[0], str):
            ability_ids = list()
            for a in aura_list:
                ability_ids += self._report.get_ability(a)
        else:
            ability_ids = aura_list

        auras = self.auras[fight_id]
        auras = [e for e in auras if e.abilityGameID in ability_ids and e.type_ in self.APPLIES]
        return EventList(list(reversed(auras)), self._report)

    def aura_on(self, aura_name: str, fight_id: int) -> list[str]:
        """List of targets of an aura"""
        # targets = map(lambda x: self._report.get_actor(x.target).name, self.auras(aura_name, fight_id))
        # return list(targets)
        return self.aura(aura_name, fight_id).named().to_targets()




