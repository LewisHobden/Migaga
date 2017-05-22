from discord.ext import commands
from cogs.utilities import credential_checks
from cogs.games.currency import connectToDatabase

import discord
import datetime
import logging
import urllib
import json

log = logging.getLogger(__name__)

class Smash:
	"""Super Smash Bros for Wii U  frame data and calculations."""
	def __init__(self, client):
		self.client = client
		self.cache  = {}
			
	API_URL = "http://api.kuroganehammer.com/api/"
	
	@commands.command(pass_context=True)
	async def attack(self,ctx,*,character_name):
		"""Gets the frame data for a certain move. Tell it the character name and then the move in a follow up."""
		character_name = character_name.replace(" ","")
		try:
			response = self.cache[character_name]["detailedmoves"]
		except KeyError:
			request_url    = self.API_URL+"characters/name/{}/detailedmoves/".format(character_name)
			response       = json.loads(urllib.request.urlopen(request_url).read().decode('utf-8'))
			response       = response
			self.cache[character_name] = {"detailedmoves" : response}
		
		await self.client.say("What move would you like to look for?")
		req_move = await self.client.wait_for_message(author=ctx.message.author)
		req_move = req_move.content.strip()
		
		for move in response:
			if move["moveName"] == req_move:
				await self.client.say(move)
				return
				
		await self.client.say("That move couldn't be found!")
	
def setup(client):
		client.add_cog(Smash(client))
	