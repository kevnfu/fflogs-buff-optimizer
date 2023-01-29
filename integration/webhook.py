from __future__ import annotations
from report.data import EventList

import discord

# see available arguments at
# https://discordpy.readthedocs.io/en/stable/api.html?highlight=embed#discord.Embed.type

class Webhook:
    def __init__(self, url):
        self.webhook = discord.SyncWebhook.from_url(url)

    def send(self, data: str, **kwargs):
        embed = discord.Embed(description=data, **kwargs)
        self.webhook.send(embed=embed)

    def send_links(self, events: EventList, **kwargs):
        data = ' '.join([f'[{e[1]}]({e[0]})' for e in events])
        self.send(data, **kwargs)