from __future__ import annotations
from typing import Any

from enums import Encounter, ReportCodes, Yoon

from config import CLIENT_ID, CLIENT_SECRET
from client import FFClient
from report import Report
from data import EventList

class FightCheck:
    class Mit:
        DEBUFFS = set(['Reprisal', 'Feint', 'Addle'])
        # DEBUFFS = set([7535, 1001193, 7549, 1001195, 7560, 10012030])

        def __init__(self, fc: FightCheck) -> None:
            self.fc = fc
            self._r = fc._r
            self._am = fc._am
            self.fight = fc.fight
            self.events = fc.events

        def at(self, boss_cast: str, occurance: int=0) -> Mit:
            self.event_name = boss_cast
            try:
                events = self.events.casts(boss_cast)
                # sometimes boss casts will have two events, an incorrect one targeting themselves.
                events = [*filter(lambda x: x.source!=x.target, events)]
                
                self.event = events[occurance]
            except IndexError:
                pass
            return self

        def at_event(self, event: EventList | Event) -> Mit:
            try:
                if isinstance(event, EventList):
                    self.event_name = event.named()[0].abilityGameID
                    self.event = event[0]
                else:
                    self.event_name = self._r.get_ability_name(event.abilityGameID)
                    self.event = event
            except IndexError:
                pass
            return self

        def all_have(self, mit_list: list[str]):
            self.mit_list = mit_list
            self.players = self.fight.players
            return self

        def has(self, player: str | list[str], mit_list: list[str]):
            self.mit_list = mit_list
            if isinstance(player, list):
                self.players = list()
                for name in player:
                    self.players += self._r.get_actor_ids(name)
            else:
                self.players = self._r.get_actor_ids(player)
            return self

        def check(self, f: File) -> None:
            try:
                time = (self.event.time - self.fight.start_time)/1000
                seconds = time % 60
                minutes = int(time / 60)
                f.write(f'{self.event_name.upper()} @ {minutes:02d}:{seconds:03.1f}')
            except AttributeError:
                f.write(f'No event\n')
                return

            mit_list = set(self.mit_list + ['Well Fed'])
            debuffs = mit_list & self.DEBUFFS
            buffs = mit_list - self.DEBUFFS

            active_auras = self._am.active_at(self.event, named=True) # active auras is by id
            
            missing = dict()

            # boss should have debuffs
            boss_id = self.event.source
            boss_name = self._r.get_actor(boss_id).name
            boss_missing = debuffs - set(active_auras.get(boss_name, list()))
            missing[boss_name] = boss_missing

            # players should have buffs
            for player_id in self.players:
                player_name = self._r.get_actor(player_id).name
                player_auras = active_auras.get(player_name, list())
                player_missing = buffs - set(player_auras)
                missing[player_name] = player_missing

            # fights include some random things as friendly players
            missing.pop('Multiple Players', None)
            missing.pop('Limit Break', None)

            if sum([len(v) for v in missing.values()])==0:
                f.write(' Good!\n')
            else:
                for k, v in missing.items():
                    if v:
                        f.write(f'\n{v} missing from {k}')
                f.write('\n')

    def __init__(self, report: Report):
        self._r = report
        self._am = report.am

    def mit(self):
        return FightCheck.Mit(self)

    def passed(self, boss_cast: str) -> bool:
        return len(self.events.casts(boss_cast)) > 0

    def run(self, fight_id: int) -> bool:
        """Returns true if success, false if failure"""
        raise NotImplementedError('Run subclass')

class FightCheckDsu(FightCheck):
    def __init__(self, report: Report):
        if report.encounter is not Encounter.DSU:
            raise TypeError(f'Using DSU checker for {encounter=}')
        super().__init__(report)

    def run(self, fight_id: int) -> None:
        self.fight = self._r.fight(fight_id)
        self.events = self._r.events(fight_id)
        if self.fight is None or self.events is None:
            print("No fight/events")
            return False

        tank1 = 'Daellin Kannose'
        tank2 = 'Pamella Royce'

        with open('checker.txt', 'w') as f:
            f.write(f'{self.fight.i=}\n')
            if self.fight.last_phase == 0: return # ignore door
            self.p2_thordan(f)
            if self.fight.last_phase == 1: return # p2
            self.p3_nidhogg(f)
            if self.fight.last_phase == 2: return
            self.p4_eyes(f)
            if self.fight.last_phase == 3: return
            self.i1_intermission(f)
            if self.fight.last_phase == 4: return
            self.p5_thordan(f)

        return True


    def p2_thordan(self, f: File) -> None:
        self.mit().at("Ascalon's Might", 0)\
            .has('Daellin Kannose', [
                'Rampart',
                'Oblation',
                'Reprisal',
                'Heart of Corundum',
                'Blackest Night'
            ]).check(f)

        self.mit().at("Ascalon's Might", 1)\
            .has('Daellin Kannose', [
                'Rampart',
                'Oblation',
                'Reprisal',
                'Heart of Corundum',
            ]).check(f)

        self.mit().at("Ascalon's Might", 2)\
            .has('Daellin Kannose', [
                'Rampart',
                'Oblation',
                'Reprisal',
                'Heart of Corundum',
            ]).check(f)

        self.mit().at('Ancient Quaga', 0)\
            .all_have([
                'Collective Unconscious',
                'Heart of Light',
                'Magick Barrier',
                'Reprisal',
                'Addle',
                'Feint',
                # 'Eukrasian Prognosis'
            ]).check(f)

        self.mit().at('Heavenly Heel', 0)\
            .has('Daellin Kannose', [
                'Shadow Wall',
                'Oblation',
                'Exaltation',
                'Reprisal',
                'Heart of Light',
                'Blackest Night'
            ]).check(f)

        self.mit().at("Ascalon's Might", 3)\
            .has('Pamella Royce', [
                'Rampart',
                'Camouflage',
                'Nebula',
                'Oblation',
                'Reprisal',
                'Heart of Corundum',
            ]).check(f)

        self.mit().at("Ascalon's Might", 4)\
            .has('Pamella Royce', [
                'Rampart',
                'Camouflage',
                'Nebula',
                'Oblation',
                'Reprisal',
                'Heart of Corundum',
            ]).check(f)

        self.mit().at("Ascalon's Might", 5)\
            .has('Pamella Royce', [
                'Rampart',
                'Camouflage',
                'Nebula',
                'Oblation',
                'Reprisal',
                'Heart of Corundum',
            ]).check(f)

        self.mit().at('Ultimate End')\
            .all_have([
                'Kerachole',
                'Dark Missionary',
                'Collective Unconscious',
                'Reprisal',
                'Addle',
                'Feint',
                'Eukrasian Prognosis'
            ]).check(f)

    def p3_nidhogg(self, f: File) -> None:
        self.mit().at('Final Chorus')\
            .all_have([
                'Kerachole',
                'Heart of Light',
                'Holos',
                'Magick Barrier',
                'Improvised Finish',
                'Eukrasian Prognosis'
            ]).check(f)

        # WYRMHOLE
        f.write('\nWYRMHOLE\n')
        if len(self.events.casts('Dive from Grace')) <= 0:
            f.write('not reached\n')
            return

        first_in_line = self._am.aura_on('First in Line', self.fight.i)
        f.write(f'{first_in_line=}\n')

        second_in_line = self._am.aura_on('Second in Line', self.fight.i)
        f.write(f'{second_in_line=}\n')

        third_in_line = self._am.aura_on('Third in Line', self.fight.i)
        f.write(f'{third_in_line=}\n')

        up_arrow = self._am.aura_on('Elusive Jump Target', self.fight.i)
        down_arrow = self._am.aura_on('Spineshatter Dive Target', self.fight.i)
        f.write(f'{up_arrow=}\n')
        f.write(f'{down_arrow=}\n')

        self.mit().at('Eye of the Tyrant', 0)\
            .all_have([
                'Shield Samba',
                'Reprisal',
                'Feint',
                'Neutral Sect',
                # 'Eukrasian Prognosis'
            ]).check(f)

        self.mit().at('Eye of the Tyrant', 1)\
            .all_have([
                'Kerachole',
                'Dark Missionary',
                'Reprisal',
                'Addle',
                'Feint',
                # 'Eukrasian Prognosis',
                # 'Collective Unconscious'
            ]).check(f)

        # 4 towers-not implemented

        tether = self.events.casts('Soul Tether')
        self.mit().at_event(tether.to('Daellin Kannose'))\
            .has('Daellin Kannose', [
                'Rampart',
                'Shadow Wall',
                'Dark Mind',
                'Oblation',
                'Blackest Night',
                'Kerachole'
            ]).check(f)

        self.mit().at_event(tether.to('Pamella Royce'))\
            .has('Pamella Royce', [
                'Rampart',
                'Camouflage',
                'Nebula',
                'Oblation',
                'Heart of Corundum',
                'Exaltation',
                'Kerachole'
            ]).check(f)

    def p4_eyes(self, f: File) -> None:
        f.write('\nEYES\n')
        red = self._am.aura('Clawbound', self.fight.i)
        initial_red = red[0:4].named().to_target()
        f.write(f'{initial_red=}\n')

        # first 2 casts are non-damaging
        dives = self.events.casts('Mirage Dive')[2:]
        dive_targets = dives.named().to_target()

        red = self._am.applied_at(dives[0]).ability('Clawbound')
        red = red.named().to_target()
        f.write(f'{red=}\n')
        f.write(f'First dives: {dive_targets[0:2]}\n')
        red = self._am.applied_at(dives[2]).ability('Clawbound')
        red = red.named().to_target()
        f.write(f'{red=}\n')
        f.write(f'Second dives: {dive_targets[2:4]}\n')
        red = self._am.applied_at(dives[4]).ability('Clawbound')
        red = red.named().to_target()
        f.write(f'{red=}\n')
        f.write(f'Third dives: {dive_targets[4:6]}\n')

    def i1_intermission(self, f: File) -> None:
        f.write('\nINTERMISSION\n')
        brightwing = self.events.casts('Brightwing')
        brightwing_order = brightwing.named().to_target()
        f.write(f'{brightwing_order=}\n')
        self.mit().at_event(brightwing.to(brightwing_order[0]))\
            .has(brightwing_order[0:2],
                ['Dark Force', 'Gunmetal Soul']
            ).check(f)
        self.mit().at_event(brightwing.to(brightwing_order[2]))\
            .has(brightwing_order[2:4],
                ['Riddle of Earth', 'Kerachole', 'Oblation', 'Exaltation']
            ).check(f)
        self.mit().at_event(brightwing.to(brightwing_order[4]))\
            .has(brightwing_order[4:6],
                ['Heart of Light', 'Dark Missionary', 'Oblation', 'Heart of Corundum']
            ).check(f)
        self.mit().at_event(brightwing.to(brightwing_order[6]))\
            .has(brightwing_order[6:8],
                ['Heart of Light', 'Dark Missionary', 'Reprisal']
            ).check(f)

        self.mit().at('Pure of Heart')\
            .all_have([
                'Dark Missionary',
                'Heart of Light',
                'Magick Barrier',
                'Reprisal',
                'Addle',
                'Feint',
                'Collective Unconscious'
            ]).check(f)

    def p5_thordan(self, f: File):
        f.write('\nThordan II\n')
        f.write('Wrath of the Heavens\n')

        lightning = self._am.aura_on('Thunderstruck', self.fight.i)
        defamation = self.events.casts('Skyward Leap').in_phases("P5").named().to_target()
        tethers = self.events.casts('Spiral Pierce').named().to_target()
        liquid_heaven = self.events.ability('Liquid Heaven')\
            .types("calculateddamage").named().to_target()
        # cauterize doesn't have target information
        # altar fire doesn't have target information

        f.write(f'{lightning=}\n')
        f.write(f'{defamation=}\n')
        f.write(f'{tethers=}\n')
        f.write(f'{liquid_heaven=}\n')

        self.mit().at("Ascalon's Mercy Revealed")\
            .all_have(['Shield Samba', 'Eukrasian Prognosis']).check(f)

        self.mit().at('Ancient Quaga', 1)\
            .all_have([
                'Heart of Light',
                'Dark Missionary',
                'Magick Barrier',
                'Collective Unconscious',
                'Reprisal',
                'Feint',
                'Addle',
                'Eukrasian Prognosis'
            ]).check(f)

        f.write('\nDeath of the Heavens\n')

        dooms = self._am.aura_on('Doom', self.fight.i)
        f.write(f'{dooms=}\n')

        self.mit().at('Heavensflame')\
            .all_have(['Kerachole', 'Panhaima', 'Eukrasian Prognosis']).check(f)

        self.mit().at('Ancient Quaga', 2)\
            .all_have([
                'Heart of Light',
                'Dark Missionary',
                'Kerachole',
                'Shield Samba',
                'Collective Unconscious',
                'Reprisal',
                'Feint',
                'Addle',
                'Eukrasian Prognosis'
            ]).check(f)


# Heavenly Heel 1:
# Both tanks kitchen sink

# Death of the Heavens

# Before going out:
# Shields
# Kerachole
# Panhaima

# Chains + Explosions Mit:
# Shields
# Holos

# Heavenly Heel 2:
# Living Dead 



reportCode = ReportCodes.JULY26.value
fight_id = 43

# client = FFClient(CLIENT_ID, CLIENT_SECRET)
# report = Report(reportCode, client, Encounter.DSU)
# checker = FightCheckDsu(report)
# checker.execute(fight_id)

