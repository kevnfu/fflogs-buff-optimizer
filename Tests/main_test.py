import pytest

from client.client import FFClient
from report.queries import Q_FIGHTS
from report.report import Report
from report.enums import Encounter

@pytest.fixture(scope="module")
def report_code():
    return 'YaAhTkyzxRjq4wKW' # Aug 16

@pytest.fixture(scope="module")
def client():
    return FFClient()

@pytest.fixture(scope="module")
def report(client, report_code):
    return Report(report_code, client, Encounter.DSU)

def test_client(client, report_code):
    res = client.q(Q_FIGHTS, {
        'reportCode': report_code,
        'fightIDs': [2]
        }, cache=False)
    res = res['reportData']
    expected = {'report': {'fights': [{'id': 2, 'encounterID': 1065, 'startTime': 2211161, 'endTime': 2379882, 'fightPercentage': 90.85, 'lastPhaseAsAbsoluteIndex': 0, 'friendlyPlayers': [157, 156, 155, 154, 153, 152, 23, 150, 82]}]}}
    assert res == expected

def test_report(report):
    report.fight(2)