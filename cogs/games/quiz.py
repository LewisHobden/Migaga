from discord.ext import commands
from cogs.utilities import credential_checks
from cogs.games.currency import Money
from cogs.games.currency import connectToDatabase

import discord
import datetime
import logging
import pymysql
import random
import time

log = logging.getLogger(__name__)

class Quiz:

	def __init__(self, client):
		self.client = client
		
	@commands.command(pass_context=True)
	async def quiz(self,ctx):
		'''Quiz yourself! How much do you know?'''
		connection = connectToDatabase()
		
		try:
				with connection.cursor() as cursor:
					sql = "SELECT COUNT(*) as `total` FROM `discord_quiz_questions` WHERE `server_id` = %s"
					cursor.execute(sql, (ctx.message.server.id))
					result = cursor.fetchone()
					
					await self.client.say("```\nQuery:"+sql.format(ctx.message.server.id)+"\nServer ID: "+ctx.message.server.id+"\nResponse: "+str(result['total'])+"\nAs type: "+str(type(result))+"```")
		finally:
			connection.close()
		
		if 0 == result:
			await self.client.say("There are no quiz questions in your server yet! Contact the server admin and get that sorted!")
			return
		
		questionChoice = questions[random.randint(0, len(questions) - 1)]
		questionSeperator = questionChoice.find("|")
		timeSeperator = questionChoice.find("-")

		questionBody = questionChoice[:questionSeperator - 1].strip()
		answer = questionChoice[questionSeperator + 1:timeSeperator - 1].strip()
		time = questionChoice[timeSeperator + 1:].strip()

		await client.say(ctx.message.author.mention + ", " + questionBody + " \nYou have " + time + " seconds to answer.")
		theirAnswer = await client.wait_for_message(author=ctx.message.author, timeout=int(time))

		try:
			theirAnswer.content = theirAnswer.content.lower()
			if theirAnswer.content.strip() == answer:
				await client.say("★ Congratulations " + ctx.message.author.mention + " you answered correctly! ★")
				await client.say("You will be awarded 50 gold!")
				original = await countRupees(ctx.message.author.id)
				awarded = int(original) + 50
				await addRupees(ctx.message.author.id, awarded)
			else:
				original = await countRupees(ctx.message.author.id)
				awarded = int(original) - 50
				await addRupees(ctx.message.author.id, awarded)
				await client.say(ctx.message.author.mention + " oh no! That was not the correct answer! -50 gold for you :(")
		except AttributeError:
				original = await countRupees(ctx.message.author.id)
				awarded = int(original) - 50
				await addRupees(ctx.message.author.id, awarded)
				await client.say(ctx.message.author.mention + " you ran out of time, that is unfortunate. Still -50 gold :c")

def setup(client):
	client.add_cog(Quiz(client))
