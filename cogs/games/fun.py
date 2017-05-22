from discord.ext import commands
from cogs.games.currency import Money

import discord
import datetime
import asyncio
import logging
import pymysql
import random
import time
import re

import json
from urllib.request import urlopen, Request

class Fun:
	""" Silly, assorted commands. """
	def __init__(self, client):
		self.client = client

	@commands.command()
	async def choose(self, *, message : str):
		""" Choose between things (separate with a comma) """
		choices = message.split(", ")
		await self.client.say("Alright. I choose.. \n:speech_balloon: **"+random.choice(choices)+"**")

	@commands.command(pass_context=True)
	async def define(self, ctx, *, query : str):
		""" Get the Urban Dictionary definition for a word """
		url		 = "http://api.urbandictionary.com/v0/define?term={0}".format(query)
		response = json.loads(urlopen(url, timeout = 15).read().decode('utf-8'))
		result	 = response["list"][0]
		
		embed = discord.Embed(title=result["word"], description=result["definition"], url=result["permalink"], color=discord.Color("15899433"))
		embed.add_field(name="Thumbs Up", value=result["thumbs_up"])
		embed.add_field(name="Source", value="Urban Dictionary")
		embed.add_field(name="Thumbs Down", value=result["thumbs_down"])

		await self.client.send_message(ctx.message.channel, embed=embed)

	@commands.command(pass_context=True)
	async def remindme(self, ctx, *, request : str):
		""" Get the bot to remind you of something in an amount of time. """
		person = ctx.message.author
		time   = request[request.find("in")+3:request.find("to")]
		thing  = request[request.find("to")+3:]

		days_to_search	  = re.search("(\S+\s+|^)days", time)
		hours_to_search	  = re.search("(\S+\s+|^)hours", time)
		minutes_to_search = re.search("(\S+\s+|^)minutes", time)
		terms = []

		if None != days_to_search:
			days = int(days_to_search.group(0)[:-5])*86400
			terms.append(days)
		if None != hours_to_search:
			hours = int(hours_to_search.group(0)[:-6])*3600
			terms.append(hours)
		if None != minutes_to_search:
			minutes = int(minutes_to_search.group(0)[:-8])*60
			terms.append(minutes)
		try:
			seconds = int(re.search("(\S+\s+|^)seconds", time).group(0)[:-8])
			terms.append(seconds)
		except:
			pass

		if(len(terms) == 0):
			await self.client.say("Cannot detect any time phrases. Set time phrases using `days`, `hours`, `minutes` and `seconds`.")
			return
		
		total = sum(terms)

		await self.client.say("So, I'll remind you in "+str(total)+" seconds to "+str(thing))
		await asyncio.sleep(total)
		await self.client.say(person.mention+" this is your reminder to "+thing+"!")
		
	@commands.command()
	async def cat(self):
		''' Type this to get a cute picture of a cat! '''
		url = "http://random.cat/meow/"
		response = urlopen(url).read()

		response = str(response)
		response = response[11:].replace("\/", "/").replace('"}', '').replace("'", "").replace("\/", "/")
		await self.client.say(response)
		
	@commands.command(pass_context=True)
	async def dog(self,ctx):
		''' Random dog pictures! So sweet. '''
		url = "http://www.randomdoggiegenerator.com/randomdoggie.php"
		req = Request(url, None, {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'})
		response = urlopen(req)
		output = open("aww.jpg","wb")
		output.write(response.read())
		await self.client.send_file(ctx.message.channel,open("aww.jpg","rb"))

	@commands.command(pass_context=True)
	async def kitten(self,ctx):
		''' Random kitten pictures! So sweet. '''
		url = "http://www.randomkittengenerator.com/cats/rotator.php"
		req = Request(url, None, {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'})
		response = urlopen(req)
		output = open("awwh.jpg","wb")
		output.write(response.read())
		await self.client.send_file(ctx.message.channel,open("awwh.jpg","rb"))
		

def setup(client):
	client.add_cog(Fun(client))
