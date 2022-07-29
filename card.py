from __future__ import annotations

from config import CLIENT_ID, CLIENT_SECRET
from client import FFClient
from enums import Encounter, Platform, ReportCodes, Yoon, Anna, Mira
from report import Report

class CardPlay:
    pass

class CardAnalyzer:
    CARD_PLAY_IDS = [
        1001883, # the bole
        1001886, # the ewer
        1001887, # the spire
        1001882, # the balance
        1001884, # the arrow
        1001885, # the spear
        4401, # the balance
        4402, # the arrow
        4403, # the spear
        4404, # the bole
        4405, # the ewer
        4406 # the spire
    ]

    def __init__(self, report: Report):
        self._r = report
        self._am = report.am

    def get_plays(self):
        self._am

video = Yoon.JULY26
client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = Report(video.code, client, Encounter.DSU)

