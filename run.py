from __future__ import annotations

import json
from operator import itemgetter

from client.client import FFClient
from report.data import EventList
from report.enums import *
from report.report import Report

from report.queries import Q_EVENTS, Q_ABILITIES, Q_FIGHTS

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

report = Report(ReportCodes.OMEGA_1.value, client, Encounter.OMEGA)

report.set_vod(Mira.OMEGA_1)
