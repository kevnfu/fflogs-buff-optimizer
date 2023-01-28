from __future__ import annotations
from report.data import EventList

import discord
from config import WEBHOOK_URL

webhook = discord.SyncWebhook.from_url(WEBHOOK_URL)

# see available arguments at
# https://discordpy.readthedocs.io/en/stable/api.html?highlight=embed#discord.Embed.type

def send(data: str, **kwargs):
    embed = discord.Embed(description=data, **kwargs)
    webhook.send(embed=embed)

def send_links(events: EventList, **kwargs):
    data = ' '.join([f'[{e[1]}]({e[0]})' for e in events])
    send(data, **kwargs)