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
        v = v['AUG09']
        assert v.code == report.code
        report.set_vod(v)

        links += events.links()

    links.sort(key=itemgetter(1))

    for i in links:
        print(i[0])

# report_code = ReportCodes.AUG02.value

client = FFClient()
report = Report(ReportCodes.AUG09.value, client, Encounter.DSU)

wrath = report.events().casts("Wrath of the Heavens")

loop_povs([Anna], report, wrath)
# for i in wrath.links():
#     print(i[0])


client.save_cache()


