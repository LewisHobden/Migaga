from discord.ext import commands
from cogs.utilities import credential_checks
from cogs.games.currency import connectToDatabase

from cogs.storage.database import Database
import discord
import datetime
import logging

log = logging.getLogger(__name__)

class Admin:
	"""Moderation related commands."""
	def __init__(self, client):
		self.client = client

	@commands.command(is_disabled=True)
	async def invite(self):
		""" Get a URL to invite the bot to your own server! """
		await self.client.say(discord.utils.oauth_url(self.client.client_id))

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

	@commands.command(no_pm=True,pass_context=True)
	@credential_checks.hasPermissions(manage_roles=True)
	async def unflaired(self,ctx):
		unflaired_users = []
		for member in ctx.message.server.members:
			if len(member.roles) == 1:
				unflaired_users.append(member)

		try:
			await self.client.say("There are "+str(len(unflaired_users))+" without a role in this server.\n")
			message = "Members:\n"
			for member in unflaired_users:
				message += member.mention+"\n"
			await self.client.say(message)
		except:
			await self.client.say("Something went wrong! Perhaps there were too many people?")

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
	async def addrole(self,ctx,*,role_name):
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

		database = Database()

		with connection.cursor() as cursor:
			sql = "SELECT * FROM `discord_role_aliases` WHERE `role_id`=%s"

			#try:
			cursor.execute(sql, [assign_role.id])
			result = cursor.fetchone()
			if None == result:
				print("This shit don't exist yo")
			else:
				await self.client.say("This role already has an alias, it is "+result['alias']+" this command will override it.")
				database.query("DELETE FROM `discord_role_aliases` WHERE `role_id`=%s",assign_role.id)

		database.query("INSERT INTO `discord_role_aliases` VALUES (0, %s, %s, %s, '0','0');",[alias,assign_role.id,server.id])

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

		with connection.cursor() as cursor:
			sql = "SELECT `role_id`,`is_admin_only` FROM `discord_role_aliases` WHERE `server_id`=%s AND `alias`=%s"
			cursor.execute(sql, [message.server.id,role])
			result = cursor.fetchone()

		if not result:
			return

		role = discord.utils.get(message.server.roles, id=str(result['role_id']))
		await self.client.add_roles(message.author,role)

		with connection.cursor() as cursor:
			sql = "UPDATE `discord_role_aliases` SET `uses`=`uses`+1 WHERE `server_id`=%s AND `role_id`=%s"
			cursor.execute(sql, [message.server.id,role.id])
			result = cursor.fetchone()

		try:
			with connection.cursor() as cursor:
				sql = "SELECT `overwrite_role_id` FROM `discord_role_overwrites` WHERE `role_id`=%s"
				cursor.execute(sql, [role.id])
				overwrites = cursor.fetchall()
		finally:
			connection.commit()
			connection.close()

	@commands.command(no_pm=True,pass_context=True)
	@credential_checks.hasPermissions(kick_members=True)
	async def names(self,ctx,member : discord.Member):
		""" See the history of name changes the bot has for a person.

		You must have kick members permission to do this."""
		connection = connectToDatabase()
		with connection.cursor() as cursor:
			sql = "SELECT `name` FROM `discord_username_changes` WHERE `user_id`=%s"
			cursor.execute(sql, [member.id])
			names = cursor.fetchall()

			msg = ""

			for name in names:
				   msg += name['name']+"\n"

		if("" == msg):
			msg = "No name changes found."
		else:
			msg = "These are the name changes I have stored: \n"+msg;

		await self.client.say(msg)

	async def findRoleByName(self,role_name,server):
		for role in server.roles:
			if role.name.lower() == role_name.lower():
				return role

		return None

	async def findRoleById(self,id,server):
		for role in server.roles:
			if str(role.id) == str(id):
				return role

		return None

	@commands.command(no_pm=True, pass_context=True)
	@credential_checks.hasPermissions(manage_messages=True,add_reactions=True)
	async def react(self,ctx,emoji : str,channel : discord.Channel, limit=50):
		""" Reacts to messages in the channel. """
		# A quick and dirty way of handling custom emoji.
		if(emoji.startswith("<")):
			emoji = emoji.replace(":","",1).replace("<","").replace(">","")

		if limit > 100:
			await self.client.say("Discord Bots are only allowed to get 100 messages at a time.")
			return

		get_message = self.client.get_cog("GetMessages")
		data = await get_message.getMessages(channel.id,limit)

		for x in data:
			message = self.client.connection._create_message(channel=channel,**x)
			await self.client.add_reaction(message,emoji)

	@commands.command(no_pm=True, pass_context=True)
	@credential_checks.hasPermissions(manage_messages=True,add_reactions=True)
	async def clearreacts(self,ctx,channel : discord.Channel, emoji : str=None, user : discord.User = None, limit=50):
		""" Clears reactions to messages in the channel.

		If an emoji is provided then it will clear all reactions of a specific emoji. However due to a limitation with Discord it can only remove the messages by the bot, or a provided user."""
		# A quick and dirty way of handling custom emoji.
		if(emoji and emoji.startswith("<")):
			emoji.replace(":","").replace("<","").replace(">","")

		if limit > 100:
			await self.client.say("Discord Bots are only allowed to get 100 messages at a time.")
			return

		get_message = self.client.get_cog("GetMessages")
		data = await get_message.getMessages(channel.id,limit)

		for x in data:
			message = self.client.connection._create_message(channel=channel,**x)
			if(emoji):
				await self.client.remove_reaction(message,emoji,user if user else self.client.user)
			else:
				await self.client.clear_reactions(message)

	@commands.command(no_pm=True,pass_context=True)
	@credential_checks.hasPermissions(manage_roles=True)
	async def roleoverwrites(self,ctx,*,role_name):
		"""When a role has been assigned a command, any overwrite will remove that role when the command is used.

		If you have roles with the same name the last one will be chosen.
		You must have the "Manage Roles" privilege in order to use this command."""
		server = ctx.message.server
		assign_role = None
		for role in server.roles:
			if role.name.lower() == role_name.lower():
				assign_role = role

		if assign_role == None:
			await self.client.say("This role could not be found.")
			return

		await self.client.say("Reply with the names of the roles you want to find here. If you want to overwrite more than one, seperate it with a comma.")
		choices = await self.client.wait_for_message(author=ctx.message.author)

		choices = choices.content.split(",")
		for role_name in choices:
			chosen_role = await self.findRoleByName(role_name.strip(),server)

			if None == chosen_role or chosen_role == assign_role:
				continue

			connection = connectToDatabase()
			with connection.cursor() as cursor:
				sql = "INSERT INTO `discord_role_overwrites` VALUES(0,%s,%s,%s)"
				cursor.execute(sql,[assign_role.id,chosen_role.id,server.id])
				connection.commit()

		connection.close()
		await self.client.say("Done! Roles will be overwritten when they use the command.")

	@commands.command(no_pm=True,hidden=True,pass_context=True)
	@credential_checks.hasPermissions(manage_roles=True)
	async def roleinfo(self,ctx,*,role_name):
		"""Get information on a role

		If you have roles with the same name the last one will be chosen.
		You must have the "Manage Roles" privilege in order to use this command."""
		server = ctx.message.server
		assign_role = None
		for role in server.roles:
			if role.name.lower() == role_name.lower():
				assign_role = role

		if assign_role == None:
			await self.client.say("This role could not be found.")
			return

		connection = connectToDatabase()
		try:
			with connection.cursor() as cursor:
				sql = "SELECT * FROM `discord_role_aliases` WHERE `server_id`=%s AND `role_id`=%s"
				cursor.execute(sql, [server.id,assign_role.id])
				result = cursor.fetchone()
		finally:
			connection.close()

		total_users = 0
		for member in server.members:
			if assign_role in member.roles:
				total_users = total_users + 1

		embed = discord.Embed(title=assign_role.name,colour=assign_role.colour,description="Role information for \""+assign_role.name+"\"")
		embed.add_field(name="Members",value=total_users)
		embed.add_field(name="Can be mentioned?",value="Yes" if assign_role.mentionable else "No")
		embed.add_field(name="Created",value=assign_role.created_at.strftime("%d of %b (%Y) %H:%M:%S"))

		if result:
			embed.add_field(name="Command Name",value=result['alias'])
			embed.add_field(name="Command Uses",value=result['uses'])

		await self.client.send_message(ctx.message.channel,embed=embed)

	@commands.command(no_pm=True,hidden=True,pass_context=True)
	@credential_checks.hasPermissions(manage_messages=True)
	async def purge(self,ctx,number_of_messages : int):
		"""Delete a number of messages from the channel you type it in!"""
		try:
			await self.client.purge_from(ctx.message.channel,limit=number_of_messages+1)
		except:
			await self.client.say("There was an error deleting. Be aware that Discord does not allow bots to bulk delete messages that are under 14 days old.")

	@commands.command(no_pm=True,hidden=True,pass_context=True)
	@credential_checks.hasPermissions(administrator=True)
	async def sql(self,ctx,*,sql):
		if ctx.message.author.id != "133736489568829440":
			return await self.client.say("Oh no, only Lewis can use this command. Far too dangerous.")

		connection = connectToDatabase()

		with connection.cursor() as cursor:
			cursor.execute(sql)

		await self.client.say("SQL executed!")

def setup(client):
		client.add_cog(Admin(client))
