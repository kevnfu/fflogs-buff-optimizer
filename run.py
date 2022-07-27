from __future__ import annotations

import json

from config import CLIENT_ID, CLIENT_SECRET
from client import FFClient
from enums import Encounter, Platform, ReportCodes, Yoon, Anna
from report import Report
from data import Event
from aura import AuraModel

from queries import Q_EVENTS


reportCode = ReportCodes.JULY26.value

client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = Report(reportCode, client, Encounter.DSU)

video = Anna.JULY26
report.set_video_offset_time(video.offset, video.fight_id)\
    .set_output_type(Platform.TWITCH, video.code)

report.deaths().to("Mayu Sakuma").links(-10000)