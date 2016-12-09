from discord.ext import commands
from cogs.utilities import credential_checks
from cogs.games.currency import Money

import discord
import datetime
import logging
import pymysql
import random
import time

class Fun:
    """ Silly, assorted commands. """
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def choose(self, *, message : str):
        choices = message.split(", ")
        await self.client.say("Alright. I choose.. \n:speech_balloon: **"+random.choice(choices)+"**")
                
def setup(client):
    client.add_cog(Fun(client))
