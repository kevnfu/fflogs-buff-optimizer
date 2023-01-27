from client.client import FFClient
from report.data import EventList
from report.enums import *
from report.report import Report

from report.queries import Q_EVENTS, Q_ABILITIES, Q_FIGHTS
client = FFClient()

def p5s():
    report = Report('8YRKtc4TjJfMdHZa', client, Encounter.P5)
    events = report.events(30)
    begin = events.by_npcs().types(['begincast'])\
        .ability([
            'Ruby Glow', 
            'Sonic Howl', 
            'Double Rush',
            'Venomous Mass',
            'Toxic Crunch',
            'Venom Squall',
            'Venem Surge',
            'Venom Pool',
            'Scatterbait',
            'Sonic Shatter',
            'Acidic Slaver'
            # 'Claw to Tail', 
            # 'Tail to Claw',
            ])\
        .filter(lambda x: not hasattr(x, 'sourceInstance'))\
        .named()

    # begin.print()
    begin.timeline()

def p6s():
    report = Report('khdMZv9K8yBGpHRb', client, Encounter.P6)
    events = report.events(69)
    
    begin = events.by_npcs().types('begincast')\
        .ability([
            'Hemitheos\'s Dark IV',
            'Chelic Synergy',
            'Synergy',
            'Unholy Darkness',
            'Pathogenic Cells',
            'Exchange of Agonies',
            'Dark Ashes',
            'Cachexia',
            'Dark Sphere',
            'Aetherial Exchange',
            'Polyominoid Sigma',
            'Choros Ixou',
            'Exocleaver'
            ])\
        .filter(lambda x: not hasattr(x, 'sourceInstance'))\
        .named()


    other = events.casts(['Ptera Ixou', 'Chelic Predation', 'Pathogenic Cells']).named()

    # casts = events.casts(['Unholy Darkness', 'Dark Ashes']).named()
    # casts.timeline()
    total = begin + other
    total.sort_time()

    total.timeline()

def p7s():

    report = Report('kH6D2fprqwYBc9Xn', client, Encounter.P7)
    events = report.events(11)
    # client.save_cache()
    begin = events.by_npcs().types('begincast')\
        .ability([
            'Spark of Life',
            'Condensed Aero II',
            'Dispersed Aero II',
            'Blades of Attis',
            'Immortal\'s Obol',
            'Forbidden Fruit',
            'Hemitheos\'s Holy III',
            'Bough of Attis',
            'Inviolate Bonds',
            'Roots of Attis',
            'Multicast',
            'Hemitheos\'s Glare',
            'Inviolate Purgation',
            'Famine\'s Harvest',
            'Death\'s Harvest',
            'War\'s Harvest',
            'Light of Life',

            ])\
        .filter(lambda x: not hasattr(x, 'sourceInstance'))\
        .named()
    other = events.casts(['Inviolate Winds', 'Chelic Predation', 'Pathogenic Cells']).named()

    total = begin + other
    total.sort_time()
    total.timeline()
    
p6s()