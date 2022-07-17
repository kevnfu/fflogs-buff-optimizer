from __future__ import annotations

import json

from config import CLIENT_ID, CLIENT_SECRET
from client import FFClient
from enums import Encounter, Platform
from report import Report, Event

def print_json(x):
    print(json.dumps(x, indent=4))

# reportCode = "yqdxtnVaHprck79W" #mira 7/14

# reportCode = "GhQRrD2kK8yB379d" # top ast clear pull 36
# fightID = 36

# reportCode = "PkaMGFgDf7hBWn2p" #mira clear pull 62
# fightID = 62

reportCode = "tbXZ3WJf9czhQyD6" # long pull 38
fightID = 38

# reportCode = "k127tNTpzycdnrVC"

client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = Report(reportCode, client, Encounter.DSU)


report.set_video_offset_time('03:19', 1) \
    .build_phase_model() \
    .print_phase_times(["P4"]) \
    .print_phase_times(["P5"])

# report.set_video_offset_time('00:21', 1) \
#     .build_phase_model() \
#     .print_phase_times_twitch(["P6"], '1533985744')


# res = client.q("""
# query {
#     reportData {
#         report(code: "rHq4kRnmKcbpgwZY") {
#             events(limit: 10000, 
#                 filterExpression: "type='targetabilityupdate'",
#                 startTime: 12957357, endTime: 13507880, fightIDs: [43]) {
#                 data
#                 nextPageTimestamp
#             }
#         }
#     }
# }
# """, {})