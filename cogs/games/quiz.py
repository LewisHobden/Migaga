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

class Quiz(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.command(pass_context=True)
	async def quiz(self,ctx):
		'''Quiz yourself! How much do you know?'''
		await self.client.send("Coming back soon, please hold tight!")
		return

		connection = connectToDatabase()

		with connection.cursor() as cursor:
			sql = "SELECT COUNT(*) as `total` FROM `discord_quiz_questions` WHERE `server_id` = %s"
			cursor.execute(sql, (ctx.message.guild.id))
			result = cursor.fetchone()

			if 0 == int(result['total']):
				await self.client.send("There are no quiz questions in your server yet! Contact the server admin and get that sorted!")
				return

			sql = "SELECT * FROM `discord_quiz_questions` WHERE `server_id` = %s"
			cursor.execute(sql, (ctx.message.guild.id))
			questions = cursor.fetchall()


		question_choice = random.choice(questions)

		question = question_choice['question']
		answer	 = question_choice['answer']
		time	 = question_choice['time_limit']

		await self.client.send(ctx.message.author.mention+", "+question+" \nYou have "+str(time)+" seconds to answer.")
		theirAnswer = await self.client.wait_for("message",check=lambda m : m.author == message.author, timeout=int(time))

		awarded = -50
		theirAnswer.content = theirAnswer.content.lower()

		try:
			if theirAnswer.content.strip() == answer:
				await self.client.send("★ Congratulations " + ctx.message.author.mention + " you answered correctly! ★\nYou will be awarded 50 gold!")
				awarded = 50
			else:
				await self.client.send(ctx.message.author.mention + " oh no! That was not the correct answer! -50 gold for you :(")
		except AttributeError:
				await self.client.send(ctx.message.author.mention + " you ran out of time, that is unfortunate. Still -50 gold :c")

		await Money.changeMoney(Money, ctx.message.author.id, int(awarded))

	@commands.command(no_pm=True, pass_context=True)
	@credential_checks.hasPermissions(manage_emojis=True)
	async def addquestion(self, ctx):
		""" Add a new quiz question to the server!

		You must have the Manage Emojis permission to do this."""
		await self.client.send("Okay, what's the question?")
		question   = await self.client.wait_for("message",check=lambda m : m.author == message.author)
		await self.client.send("Sweet. What's the answer? (Write it exactly as you want it to be answered. Case is ignored.)")
		answer	   = await self.client.wait_for("message",check=lambda m : m.author == message.author)
		await self.client.send("And the time limit in seconds?")
		time_limit = await self.client.wait_for("message",check=lambda m : m.author == message.author)

		connection = connectToDatabase()

		with connection.cursor() as cursor:
			sql = "INSERT INTO `discord_quiz_questions` VALUES (0, %s, %s, %s, %s)"
			try:
				cursor.execute(sql, [question.content,answer.content.strip().lower(),int(time_limit.content.strip()),ctx.message.guild.id])
			except:
				await self.client.send("Sorry, there was an error somewhere.. ensure you have properly provided me with information. If this problem persists contact the admin")
				return

		await self.client.send("Whew! All done! I have added the question **"+question.content+"**, with the answer: **"+answer.content.strip()+"** and a time limit of: **"+time_limit.content.strip()+"** seconds to the server **"+ctx.message.guild.name+"**")

		connection.commit()

def setup(client):
	client.add_cog(Quiz(client))
