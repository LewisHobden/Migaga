from discord.ext import commands

import discord
import datetime
import asyncio
import logging
import random
import time
import re
import json

class Starboard:
    """ Commands related to the Starboard. """
    def __init__(self, client):
        self.client = client

    async def on_socket_raw_receive(self, data):
        # no binary allowed please
        if isinstance(data, bytes):
            return

        data       = json.loads(data)
        event_name = data.get('t')
        payload    = data.get('d')
        
        if event_name == 'MESSAGE_REACTION_ADD':
            if payload['emoji']['name'] == "⭐":
                print ("Star detected")

    def loadStars():
        with open(r"C:\Development\Code\web\python-discord-bot\cogs\storage\starred-messages.json") as storage:
            return json.load(records)

    async def createEmbedForStarredMessage(messsage):
        e = discord.Embed()
        e.timestamp = message.timestamp
        author = message.author

        avatar = author.default_avatar_url if not author.avatar else author.avatar_url
        avatar = avatar.replace('.gif', '.jpg')
        e.set_author(name=author.display_name, icon_url=avatar)


    def star_emoji(self, stars):
        if 5 >= stars >= 0:
            return '\N{WHITE MEDIUM STAR}'
        elif 10 >= stars >= 6:
            return '\N{GLOWING STAR}'
        elif 25 >= stars >= 11:
            return '\N{DIZZY SYMBOL}'
        else:
            return '\N{SPARKLES}'

def setup(client):
    client.add_cog(Starboard(client))
