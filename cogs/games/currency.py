from discord.ext import commands
from cogs.utilities import credential_checks

import discord
import datetime
import logging

log = logging.getLogger(__name__)

class Money:
	"""The currency of the bot."""
	def __init__(self, client):
		self.client = client
	
	@commands.command(no_pm=True, pass_context=True)
	async def money(self, ctx):
		# Connect to Database and pull it all down
		await self.client.say("You have earned "+money+" money!")
		
	@asyncio.coroutine()
	def addMoney(user_id, money):
		# Add money to the database.
		
	

def setup(client):
        client.add_cog(Admin(client))