from discord.ext import commands
from cogs.utilities import credential_checks

from cogs.storage.database import Database

import discord
import datetime
import logging
import pymysql
import time
import asyncio

log = logging.getLogger(__name__)

class Money(commands.Cog):
	"""The currency of the bot."""
	CURRENCY_NAME = "money"

	def __init__(self, client):
		self.client	   = client
		self.database  = Database()

	@commands.command(no_pm=True, pass_context=True)
	async def money(self, ctx):
		""" See how much you have earned! """
		money = await self.checkMoney(ctx.message.author.id)
		await self.client.send("**"+ctx.message.author.name+"**, You have earned "+str(money['money'])+" "+self.CURRENCY_NAME+" after playing "+str(money['times_played'])+" games!")

	@commands.command(no_pm=True, pass_context=True)
	async def moneyfor(self, ctx, member : discord.Member):
		""" See how much somebody else has earned.

		Mention another user with it!"""
		money = await self.checkMoney(member.id)
		await self.client.send("**"+member.name+"**, You have earned "+str(money['money'])+" "+self.CURRENCY_NAME+" after playing "+str(money['times_played'])+" games!")

	@commands.command(no_pm=True, pass_context=True)
	async def give(self, ctx, recipient : discord.Member, amount):
		""" Send to another person! """
		giver		 = ctx.message.author
		giver_budget = await self.checkMoney(giver.id)

		try:
			amount = int(amount)
		except ValueError:
			await self.client.send("Please provide a real number!")
			return False
		if amount < 0:
			await self.client.send("You can't steal "+self.CURRENCY_NAME+" from others! That's not cool.")
			return False
		elif int(giver_budget['money']) < amount:
			await self.client.send("You cannot afford give that much "+self.CURRENCY_NAME+"!")
			return False

		# await self.changeMoney(giver.id, amount*-1)
		# await self.changeMoney(recipient.id, amount)

		await self.client.send("Success! I have given **"+recipient.name+"** "+str(amount)+" "+self.CURRENCY_NAME+" from **"+giver.name+"**!")

	async def changeMoney(self, user_id, money):
		sql = "INSERT INTO `discord_persons` VALUES (0, %s, %s, '1', '1') ON DUPLICATE KEY UPDATE `money`=`money`+%s, times_played=times_played+1"
		cursor = self.database.query(sql, (user_id, money, money))

	async def checkMoney(self, user_id):
		sql = "SELECT `money`, `times_played` FROM `discord_persons` WHERE `user_id`=%s"
		cursor = this.database.query(sql, user_id)
		return cursor.fetchone()

def setup(client):
	client.add_cog(Money(client))
