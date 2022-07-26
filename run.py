from __future__ import annotations

import json

from config import CLIENT_ID, CLIENT_SECRET
from client import FFClient
from enums import Encounter, Platform, ReportCodes
from report import Report
from data import Event
from aura import AuraModel

from queries import Q_EVENTS


def print_a():
    reportCode = "Tm8K39AaBpYwD4MR"

    client = FFClient(CLIENT_ID, CLIENT_SECRET)
    report = Report(reportCode, client, Encounter.DSU)
    # print_a(report)

    # anna
    report.set_video_offset_time('19:17', 2)\
        .set_output_type(Platform.TWITCH, '1537996395')\

    report.casts('Final Chorus').in_fight(33).links(-10000)

# reportCode = "GhQRrD2kK8yB379d" # top ast clear pull 36
# fightID = 36
# reportCode = "PkaMGFgDf7hBWn2p" # mira clear pull 62
# fightID = 62

reportCode = ReportCodes.JULY26.value

client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = Report(reportCode, client, Encounter.DSU)

report.set_video_offset_time('13:27', 1)\
    .set_output_type(Platform.TWITCH, 1540569628)

# report.print_phase_times(['P3'], 60000)

fight_id = 43
with open('test.json', 'w') as f:
    f.write('EVENT FILTER\n')
    x = report.events(fight_id).types("death").named().write(f)
    # f.write('INCATEGORY DEATHS\n')
    # y = report.deaths(fight_id).named().write(f)
    # print(len(x))
    # print(len(y))
# res = client.q(Q_EVENTS, params={
#     'reportCode': reportCode,
#     'encounterID': Encounter.DSU.value,
#     'startTime': 0, 
#     'endTime': 999999999999999999999999999,
#     'filter': "ability.name='ascalon's might'",
#     'fightIDs': 35})

# print(res)