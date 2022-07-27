from config import CLIENT_ID, CLIENT_SECRET
from client import FFClient
from enums import Encounter, Platform, ReportCodes,
from report import Report
from fightcheck import FightCheckDsu

reportCode = ReportCodes.JULY26.value

client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = Report(reportCode, client, Encounter.DSU)

checker = FightCheckDsu(report)

current_fight = 1
while (line:=input(f'Fight {current_fight}?')) != 'x':
    if line.isdigit():
        current_fight = int(line)

    if checker.run(current_fight):
        print(f'Finished {current_fight=}')
    else:
        print(f'failed')
