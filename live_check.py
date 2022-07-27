from config import CLIENT_ID, CLIENT_SECRET
from client import FFClient
from enums import Encounter, Platform, ReportCodes
from report import Report
from fightcheck import FightCheckDsu

reportCode = ReportCodes.JULY26.value

client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = Report(reportCode, client, Encounter.DSU)

checker = FightCheckDsu(report)

current_fight = 2
while (line:=input('Fight#?')) != 'x':
    if line.isdigit():
        current_fight = int(line)

    if report.fight(fight_id) is not None:
        checker.run(current_fight)
        print('Done')
