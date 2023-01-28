from __future__ import annotations
from report.data import EventList

# bot.py
import asyncio
import discord

from config import DISCORD_TOKEN, BOT_CHANNEL
client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    channel = client.get_channel(BOT_CHANNEL)
    # await channel.send('some stuff [google](http://www.google.com)')

# client.run(DISCORD_TOKEN)

class Bot:
    @staticmethod
    def send(data: str):
        embed = discord.Embed(description=data)
        webhook.send(embed=embed)

    @staticmethod
    def send_links(events: EventList):
        data = ' '.join([f'[{e[1]}]({e[0]})' for e in events])
        embed = discord.Embed(description=data, title="test")
        webhook.send(embed=embed)
