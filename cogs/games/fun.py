from discord.ext import commands
from cogs.utilities import credential_checks
from cogs.games.currency import Money

import discord
import datetime
import logging
import pymysql
import random
import time

import json
from urllib.request import urlopen, Request
from urllib.error import URLError


class Fun:
    """ Silly, assorted commands. """
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def choose(self, *, message : str):
        choices = message.split(", ")
        await self.client.say("Alright. I choose.. \n:speech_balloon: **"+random.choice(choices)+"**")

    @commands.command(pass_context=True)
    async def define(self, ctx, *, query : str):
        url      = "http://api.urbandictionary.com/v0/define?term={0}".format(query)
        response = json.loads(urlopen(url, timeout = 15).read().decode('utf-8'))
        result   = response["list"][0]
        
        embed = discord.Embed(title=result["word"], description=result["definition"], url=result["permalink"], color=discord.Color("15899433"))
        embed.add_field(name="Thumbs Up", value=result["thumbs_up"])
        embed.add_field(name="Source", value="Urban Dictionary")
        embed.add_field(name="Thumbs Down", value=result["thumbs_down"])

        await self.client.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def remindme(self, ctx, *, request : str):
        """ remind me in 4 hours to be a bee """
        
        
                
def setup(client):
    client.add_cog(Fun(client))
