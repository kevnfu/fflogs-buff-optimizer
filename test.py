from __future__ import annotations

import json

from config import CLIENT_ID, CLIENT_SECRET
from client import FFClient
from enums import Encounter, Platform
from phases import ReportDsu

def print_json(x):
    print(json.dumps(x, indent=4))

# reportCode = "yqdxtnVaHprck79W" #mira 7/14
# reportCode = "GhQRrD2kK8yB379d" # top ast clear pull 36
# fightID = 36
# reportCode = "PkaMGFgDf7hBWn2p" # mira clear pull 62
# fightID = 62

def print_abilities(report):
    # for my video
    report.set_video_offset_time('03:19', 1) \
        .set_output_type(Platform.YOUTUBE)
    report.print_phase_times(["P5"])

    print("double_midare")
    double_midare = report.actions("Kaeshi: Setsugekka")
    # [print(x) for x in double_midare]
    double_midare = double_midare.in_phases(["P4", "I", "P5"])
    report.output_events(double_midare, -7000, ' ')


    p_balance = report.actions("Perfect Balance").in_phases(["P3", "P5"])
    print("Perfect Balance")
    report.output_events(p_balance, -5000, ' ')

    # anna's POV
    report.set_video_offset_time('01:31', 1) \
        .set_output_type(Platform.TWITCH, '1533795273')

    print("double_midare")
    report.output_events(double_midare, -7000)

    print("wrath")
    wrath = report.actions("Wrath of the Heavens")
    report.output_events(wrath, -3700)

reportCode = "tbXZ3WJf9czhQyD6" # long pull 38
fightID = 38

client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = ReportDsu(reportCode, client, Encounter.DSU)
print_abilities(report)


