from __future__ import annotations

import json

from config import CLIENT_ID, CLIENT_SECRET
from client import FFClient
from enums import Encounter, Platform
from report import Report

from aura import AuraModel


def print_a(report):
    # for my video
    # anna
    report.set_video_offset_time('28:57', 1) \
        .set_output_type(Platform.TWITCH, '1535990224')

    # report.deaths().to("Mayu Sakuma").print()

    # yoon 
    report.set_video_offset_time('1:06', 1)\
        .set_output_type(Platform.TWITCH, '1536014750')\
        .casts('Standard Step').in_phases(['P5']).print(-5000)

# reportCode = "GhQRrD2kK8yB379d" # top ast clear pull 36
# fightID = 36
# reportCode = "PkaMGFgDf7hBWn2p" # mira clear pull 62
# fightID = 62

reportCode = "19M43vwFh6GtAcCp"

client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = Report(reportCode, client, Encounter.DSU)
# print_a(report)

# report.set_video_offset_time('1:06', 1)\
#     .set_output_type(Platform.TWITCH, '1536014750')\

# with open('test.json', 'w') as f:
#     report.print_pull_times()
#     report.actions("Ancient Quaga").in_phase("P2").named().write(f).print()

am = AuraModel(client, report)
am.test()

# Q_TABLE = """
# query Graph {
#     rateLimitData {
#         limitPerHour
#         pointsSpentThisHour
#     }
#     reportData {
#         report(code: "TwzV7fmdhpA1gykF") {
#             table( 
#                 startTime: 0, endTime: 9999999999,
#                 encounterID: 1065,
#                 filterExpression: "ability.name='Ancient Quaga'",
#                 fightIDs: [30])
#         }
#     }
# }
# """

# res = client.q(Q_TABLE, {})

# print(json.dumps(res, indent=4))