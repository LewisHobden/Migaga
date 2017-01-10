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


def setup(client):
    client.add_cog(Starboard(client))
