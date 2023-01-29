from __future__ import annotations

import json
from operator import itemgetter

from client.client import FFClient
from report.data import EventList
from report.enums import *
from report.report import Report

from report.queries import Q_EVENTS, Q_ABILITIES, Q_FIGHTS
from config import WEBHOOK_URL, WEBHOOK_URL_TEST

from integration.webhook import Webhook

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
report = Report(ReportCodes.Day2.value, client, Encounter.OMEGA)

report.set_vod(Slade.Day2)
for a in report.actors:
    print(a)

partysyn = report.begincasts("Party Synergy").by_id(25)
info = partysyn.links()

# for i in info:
#     print(f'#{i[1]}: {i[0]}')

webhook = Webhook(WEBHOOK_URL)
webhook.send_links(info, title="Queen Mira")