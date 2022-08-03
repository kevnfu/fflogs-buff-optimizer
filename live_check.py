import time

from config import CLIENT_ID, CLIENT_SECRET
from client import FFClient
from enums import Encounter, ReportCodes
from report import Report
from fightcheck import FightCheckDsu

LOOP_LIMIT = 10
THROTTLE_TIME = 3

reportCode = ReportCodes.AUG02.value

client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = Report(reportCode, client, Encounter.DSU)

last_fight_id = report.last_fight().i
counter = 0
while report.fight(last_fight_id+1) is None:
    print('No new fight found')
    time.sleep(THROTTLE_TIME)
    counter += 1
    if counter > LOOP_LIMIT:
        break

with FightCheckDsu(report) as checker:
    checker.run(last_fight_id + 1)
