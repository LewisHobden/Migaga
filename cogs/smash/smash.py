from discord.ext import commands
from cogs.utilities import credential_checks, config
from cogs.games.currency import connectToDatabase
from cogs.smash.attack import Attack
from cogs.smash.hitbox import Hitbox

import discord
import datetime
import logging
import urllib
import json
import random

log = logging.getLogger(__name__)

class Smash(commands.Cog):
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
		character_name = character_name.replace(" ","").lower()
		self.typing_channel = ctx.message.channel
		response = await self.getCharacterDetailedMoves(character_name)

		await self.client.send("What move would you like to look for?")
		req_move = await self.client.wait_for("message",check=lambda m : m.author == message.author)
		req_move = req_move.content.strip()

		possible_moves = []
		for move in response:
			if move["moveName"].lower().find(req_move.lower()) != -1:
				possible_moves.append(move)

		if [] == possible_moves:
			await self.client.send("That move couldn't be found!")
			return

		if len(possible_moves) > 1:
			clari_msg = "Multiple moves found! Reply with the move number to get its data.\n"
			i = 0
			for potential_move in possible_moves:
				i = i + 1
				clari_msg += "**"+str(i)+"**. "+potential_move['moveName']+"\n"

			await self.client.send(clari_msg)
			choice = await self.client.wait_for("message",check=lambda m : m.author == message.author)

			try:
				chosen_index = int(choice.content)
				attack = Attack(possible_moves[chosen_index-1])
			except:
				await self.client.send("Invalid number provided!")
				return
		else:
			attack = Attack(possible_moves[0])

		character_details = self.cache.get(character_name)['details']
		e = discord.Embed(title=attack.getName(),colour=int(character_details['colorTheme'].replace("#",""),16))
		e.set_author(name="Kurogane Hammer / "+character_details['displayName'],icon_url=character_details['thumbnailUrl'])
		e.set_thumbnail(url=character_details['fullUrl'])

		faf_inline = False

		if "-" != attack.getLandingLag():
			e.add_field(name="Landing Lag",value=attack.getLandingLag())
			faf_inline = True
		if "-" != attack.getLandingLag():
			e.add_field(name="Autocancel",value=attack.getAutocancel())
			faf_inline = True

		e.set_footer(text=await self.getFooterMessage())
		e.add_field(name="FAF",inline=faf_inline,value=attack.getFirstActionableFrame())

		for i in range(1,6):
			hitbox = attack.getHitbox(i)
			if False == hitbox.hasData():
				continue

			info = "Base Damage: {0}\nBase Knockback: {1}\nKnockback Growth: {2}\nAngle: {3}\nFrames Active: {4}\nNote: {5}".format(str(hitbox.getBaseDamage())+"%",hitbox.getBaseKnockback(),str(hitbox.getKnockbackGrowth()),hitbox.getAngle(),hitbox.getActiveFrames(),hitbox.getNote())
			e.add_field(name="Hitbox {}".format(i),value=info)

		await self.client.send(embed=e)

	async def getFooterMessage(self):
		responses = [
			"Info from kuroganehammer.com",
			"If FAF is empty, look for an earlier hitbox."
		]

		return random.choice(responses)


def setup(client):
		client.add_cog(Smash(client))
