from __future__ import annotations

import json
from operator import itemgetter

from config import CLIENT_ID, CLIENT_SECRET
from client import FFClient
from enums import Encounter, Platform, ReportCodes, Vod, Yoon, Anna, Mira, Kevin, Aaron, Blake, Sarah
from report import Report
from data import EventList

from queries import Q_EVENTS, Q_ABILITIES


def loop_povs(vod_list: [Vod], report: Report, events: EventList) -> None:
    links = list()
    for v in vod_list:
        v = v['AUG02']
        assert v.code == report.code
        report.set_vod(v)

        links += events.links()

    links.sort(key=itemgetter(1))

    for i in links:
        print(i[0])

report_code = ReportCodes.AUG02.value

client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = Report(report_code, client, Encounter.DSU)


wrath = report.events().casts("Wrath of the Heavens")

x = loop_povs([Anna, Kevin, Aaron],
    report, wrath)

client.save_cache()
