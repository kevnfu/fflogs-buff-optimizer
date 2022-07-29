from __future__ import annotations

import json

from config import CLIENT_ID, CLIENT_SECRET
from client import FFClient
from enums import Encounter, Platform, ReportCodes, Yoon, Anna, Mira
from report import Report
from data import Event
from aura import AuraModel

from queries import Q_EVENTS


reportCode = ReportCodes.JULY26.value

video = Mira.JULY27
client = FFClient(CLIENT_ID, CLIENT_SECRET)
report = Report(video.code, client, Encounter.DSU)

report.set_video_offset_time(video.offset, video.fight_id)\
    .set_output_type(Platform.TWITCH, video.url)

report.print_phase_times(["P6"])