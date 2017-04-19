from discord.ext import commands
from cogs.utilities import credential_checks
from cogs.games.currency import connectToDatabase

import discord
import datetime
import logging

log = logging.getLogger(__name__)

class Admin:
	"""Moderation related commands."""
	def __init__(self, client):
		self.client = client

	@commands.command(no_pm=True, pass_context=True)
	@credential_checks.hasPermissions(ban_members=True)
	async def ban(self, ctx, member : discord.Member):
		"""Bans a member from the server.
		In order to do this, the bot and you must have Ban Member permissions.
		"""
		try:
			await self.client.ban(member)
		except discord.Forbidden:
			await self.client.say("The bot does not have permissions to kick members.")
		except discord.HTTPException:
			await self.client.say("Kicking failed.")
		else:
			await self.client.say("BOOM. Banned "+member.name)

	@commands.command(no_pm=True, pass_context=True)
	@credential_checks.hasPermissions(kick_members=True)
	async def kick(self, ctx, member : discord.Member):
		"""Kicks a member from the server.
		In order to do this, the bot and you must have Kick Member permissions.
		"""
		try:
			await self.client.kick(member)
		except discord.Forbidden:
			await self.client.say("The bot does not have permissions to kick members.")
		except discord.HTTPException:
			await self.client.say("Kicking failed.")
		else:
			await self.client.say("BOOM. Kicked "+member.name)

	@commands.command(no_pm=True, pass_context=True)
	@credential_checks.hasPermissions(ban_members=True)
	async def softban(self, ctx, member : discord.Member):
		"""Bans and unbans a member from the server.
		In order to do this, the bot and you must have Ban Member permissions.

		This should be used in order to kick a member from the server whilst also
		deleting all the messages that they have sent.
		"""
		try:
			await self.client.ban(member)
			await self.client.unban(member.server, member)
		except discord.Forbidden:
			await self.client.say("The bot does not have permissions to kick members.")
		except discord.HTTPException:
			await self.client.say("Kicking failed.")
		else:
			await self.client.say("Softbanned "+member.name+". Their messages should be gone now.")
	
	@commands.command(no_pm=True, pass_context=True)
	@credential_checks.hasPermissions(manage_roles=True)
	async def registerrole(self,ctx,*,role_name):
		"""Adds a role to the bot so that it can either be self assigned by a user or given by an admin. 
		
		If you have roles with the same name the last one will be chosen.
		You must have the "Manage Roles" privilege in order to use this command."""
		server = ctx.message.server
		assign_role = None
		for role in server.roles:
			if role.name.lower() == role_name.lower():
				assign_role = role
		
		if assign_role == None:
			await self.client.say("This role could not be found and therefore could not be registered!")
			return

		await self.client.say("Role found: "+assign_role.name+", its ID is "+assign_role.id)
		await self.client.say("Okdok so, what command should be used to assign this role?")
		
		alias = await self.client.wait_for_message(author=ctx.message.author)
		alias = alias.content.lower().strip()
		
		connection = connectToDatabase()
		
		with connection.cursor() as cursor:
			sql = "INSERT INTO `discord_role_aliases` VALUES (0, %s, %s, %s, '0');"
			
			try:
				cursor.execute(sql, [alias,assign_role.id,server.id])
			except:
				await self.client.say("Sorry, there was an error somewhere.. ensure you have properly provided me with information. If this problem persists contact the admin")
				return
		
		connection.commit()
		await self.client.say("Whew! All done! I have added the role **"+assign_role.name+"**, to the alias: **"+alias+"** in this server: **"+server.name+"**")
		
	@commands.command(no_pm=True, pass_context=True)
	@credential_checks.hasPermissions(manage_server=True)
	async def welcomemessage(self,ctx,*,message):
		"""
		Creates an automatic welcome message for the bot to say when a new user joins. Use <@> for user mention, <> for user name, and <s> for the server name!
		You will be asked a follow up question for what channel the welcome message should be done into. 
		
		You must have manage server permissions to use this command. 
		"""
		message_to_store = message.replace("<@>","{0}").replace("<>","{1}").replace("<s>","{2}")
		
		connection = connectToDatabase()
		await self.client.say("What channel should that message be posted in?")
		channel    = await self.client.wait_for_message(author=ctx.message.author)
		try:
			channel = channel.channel_mentions[0]
		except:
			await self.client.say("You must mention a channel!")
			return 
		
		try:
			with connection.cursor() as cursor:
				sql = "INSERT INTO `discord_welcome_messages` VALUES (0,%s,%s,%s) ON DUPLICATE KEY UPDATE `message`=%s,`channel_id`=%s"
				cursor.execute(sql, [message_to_store,ctx.message.server.id,channel.id,message_to_store,channel.id])
				result = cursor.fetchone()
		finally:
			connection.commit()
		
		await self.client.say("Okay! I've added that welcome message to "+channel.mention+", here's an example: "+message_to_store.format(ctx.message.author.mention,ctx.message.author.display_name,ctx.message.server.name))
		
	async def checkAndAssignRole(self,role,message : discord.Message):
		member = message.author
		connection = connectToDatabase()
		try:
			with connection.cursor() as cursor:
				sql = "SELECT `role_id` FROM `discord_role_aliases` WHERE `server_id`=%s AND `alias`=%s"
				cursor.execute(sql, [message.server.id,role])
				result = cursor.fetchone()
		finally:
			connection.close()
			
		if not result:
			return
			
		role = discord.utils.get(message.server.roles, id=str(result['role_id']))
			
		await self.client.add_roles(message.author,role)
		await self.client.delete_message(message)
		
		return True
	
def setup(client):
		client.add_cog(Admin(client))
