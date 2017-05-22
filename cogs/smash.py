from discord.ext import commands
from .utilities import credential_checks, config
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
		
		# config format:
		# <character_name> : as follows ->
		# details: /api/characters/
		# detailedmoves: characters/name/{}/detailedmoves/
		self.cache = config.Config('khcache.json')
		
	API_URL      = "http://api.kuroganehammer.com/api/"
	KUROGANE_URL = "http://kuroganehammer.com/Smash4/"
	
	async def getCharacterDetails(self,character_name):
		try:
			response = self.cache.get(character_name)['details']
		except:
			await self.client.send_typing(self.typing_channel)
			request_url    = self.API_URL+"characters/name/{}/".format(character_name)
			response       = json.loads(urllib.request.urlopen(request_url).read().decode('utf-8'))
			response       = response
			
		return response
		
	async def getCharacterDetailedMoves(self,character_name):
		try:
			response = self.cache.get(character_name)['detailedmoves']
		except:
			await self.client.send_typing(self.typing_channel)
			request_url    = self.API_URL+"characters/name/{}/detailedmoves/".format(character_name)
			response       = json.loads(urllib.request.urlopen(request_url).read().decode('utf-8'))
			response       = response
			await self.cache.put(character_name,{"details" : await self.getCharacterDetails(character_name),"detailedmoves" : response})
			
		return response

	@commands.command(pass_context=True)
	async def attack(self,ctx,*,character_name):
		"""Gets the frame data for a certain move. Tell it the character name and then the move in a follow up."""
		character_name = character_name.replace(" ","")
		self.typing_channel = ctx.message.channel
		response = await self.getCharacterDetailedMoves(character_name)
		
		await self.client.say("What move would you like to look for?")
		req_move = await self.client.wait_for_message(author=ctx.message.author)
		req_move = req_move.content.strip()
		
		for move in response:
			if move["moveName"].lower() == req_move.lower():
				character_details = self.cache.get(character_name)['details']
				e = discord.Embed(title=move["moveName"],colour=int(character_details['colorTheme'].replace("#",""),16))
				e.set_author(name="Kurogane Hammer / "+character_details['displayName'],url=character_details['fullUrl'],icon_url=character_details['thumbnailUrl'])
				e.add_field(name="Base Damage",value=move['baseDamage']['hitbox1'])
				e.add_field(name="Base Knockback",value=move['baseKnockback']['hitbox1'])
				e.add_field(name="First Actionable Frame",value="Frame "+move['firstActionableFrame']['frame'])
				await self.client.say(embed=e)
				return
				
		await self.client.say("That move couldn't be found!")
	
def setup(client):
		client.add_cog(Smash(client))
	