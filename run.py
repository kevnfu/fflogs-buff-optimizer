from __future__ import annotations

import json
from operator import itemgetter

from client.client import FFClient
from report.data import EventList
from report.enums import Encounter, Platform, ReportCodes, Vod, Yoon, Anna, Mira, Kevin, Aaron, Blake, Sarah
from report.report import Report

from report.queries import Q_EVENTS, Q_ABILITIES

def loop_povs(vod_list: [Vod], report: Report, events: EventList) -> None:
    links = list()
    for v in vod_list:
        v = v['AUG16']
        assert v.code == report.code
        report.set_vod(v)

        links += events.links()

    links.sort(key=itemgetter(1))

    for i in links:
        print(i[0])

client = FFClient()

report = Report(ReportCodes.AUG16.value, client, Encounter.DSU)

wrath = report.events().casts("Death of the Heavens")

# for fight in report._fights:
#     print(fight)

loop_povs([Anna, Kevin, Aaron, Yoon], report, wrath)
# for i in wrath.links():
    # print(i[0])

# client.save_cache()


