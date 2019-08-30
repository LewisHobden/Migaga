from discord.ext import commands
from cogs.utilities import credential_checks

from model.role_alias import RoleAlias
from model.welcome_message import WelcomeMessage

from cogs.storage.database import Database
import discord
import logging

log = logging.getLogger(__name__)


class Admin(commands.Cog):
    """Moderation related commands."""

    def __init__(self, client):
        self.client = client
        self.database = Database()

    @commands.command(pass_context=True)
    async def invite(self, ctx):
        """ Get a URL to invite the bot to your own server! """
        await ctx.send(discord.utils.oauth_url(self.client.client_id))commands

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(ban_members=True)
    async def ban(self, ctx, member: discord.User, delete_message_days: int = 0, reason: str = ""):
        """Bans a member from the server. You can provide a user either by their ID or mentioning them.
        In order to do this, the bot and you must have Ban Member permissions.
        """
        try:
            await ctx.guild.ban(member, delete_message_days=delete_message_days, reason=reason)
        except discord.Forbidden:
            await ctx.send("The bot does not have permissions to kick members.")
        except discord.HTTPException:
            await ctx.send("Kicking failed. I think it was my fault.. try again?")
        else:
            await ctx.send("BOOM! Banned " + member.name)

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(ban_members=True)
    async def unban(self, ctx, member: discord.User, delete_message_days: int = 0, reason: str = ""):
        """Unbans a member from the server. You can provide a user either by their ID or mentioning them.
        In order to do this, the bot and you must have Ban Member permissions.
        """
        try:
            await ctx.guild.unban(member)
        except discord.Forbidden:
            await ctx.send("I don't have permission!.")
        except discord.HTTPException:
            await ctx.send("Something went wrong. I think it was my fault.. try again?")
        else:
            await ctx.send("Ok! Unbanned " + member.name)

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member):
        """Kicks a member from the server.
        In order to do this, the bot and you must have Kick Member permissions.
        """
        try:
            await member.guild.kick(member)
        except discord.Forbidden:
            await ctx.send("The bot does not have permissions to kick members.")
        except discord.HTTPException:
            await ctx.send("Kicking failed.")
        else:
            await ctx.send("BOOM. Kicked " + member.name)

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_roles=True)
    async def unflaired(self, ctx):
        """ Counts the total number of people without flairs in the server.

        You must have "Manage Roles" in order to run this command."""
        unflaired_users = []
        for member in ctx.message.guild.members:
            if len(member.roles) == 1:
                unflaired_users.append(member)

        plural = "people" if len(unflaired_users) > 1 else "person"
        await ctx.send("I found " + str(len(unflaired_users)) + " " + plural + " without a role in this server.\n")

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(ban_members=True)
    async def softban(self, ctx, user: discord.User, delete_message_days: int = 0, reason: str = ""):
        """Bans and unbans a member from the server. You can provide a user either by their ID or mentioning them.
        In order to do this, the bot and you must have Ban Member permissions.

        This should be used in order to kick a member from the server whilst also
        deleting all the messages that they have sent.
        """
        try:
            await ctx.guild.ban(user, delete_message_days=delete_message_days, reason=reason)
            await ctx.guild.unban(user)
        except discord.Forbidden:
            await ctx.send("I don't have permission to do this.")
        except discord.HTTPException:
            await ctx.send("Something went wrong. Seems like a problem on my end. Try again?")
        else:
            await ctx.send("Softbanned {.name}. Their messages should be gone now.".format(user))

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_roles=True)
    async def addrole(self, ctx, role: discord.Role):
        """Adds a role to the bot so that it can either be self assigned by a user or given by an admin.

        If you have roles with the same name the last one will be chosen.
        You must have the "Manage Roles" privilege in order to use this command."""
        await ctx.send("Ok! What command should be used to assign this role?")

        alias = await self.client.wait_for(
            "message",
            check=lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel)

        alias = alias.content.lower().strip()

        RoleAlias.create(alias=alias, role_id=role.id, server_id=ctx.message.guild.id, is_admin_only=False, uses=0)

        embed = discord.Embed(description="Ok! Added!", title="Role Command Added", color=discord.Colour.dark_green())
        embed.add_field(name="Role", value=role.name)
        embed.add_field(name="Command", value=alias)

        await ctx.send(embed=embed)

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_guild=True)
    async def welcomemessage(self, ctx, *, message):
        """
        Creates an automatic welcome message for the bot to say when a new user joins. Use <@> for user mention,
        <> for user name, and <s> for the server name!

        You will be asked a follow up question for what channel the welcome message should be said in.

        You must have manage server permissions to use this command.
        """
        message_to_store = message.replace("<@>", "{0}").replace("<>", "{1}").replace("<s>", "{2}")

        await ctx.send("What channel should that message be posted in?")
        channel = await self.client.wait_for(
            "message",
            check=lambda m: m.author == ctx.message.author and m.channel == ctx.channel)
        try:
            channel = channel.channel_mentions[0]
        except KeyError:
            await ctx.send("Oops! You must mention a channel!")
            return

        WelcomeMessage.create(message=message_to_store, server_id=ctx.guild.id, channel_id=channel.id)

        example = message_to_store.format(ctx.message.author.mention, ctx.message.author.display_name,
                                          ctx.message.guild.name)

        embed = discord.Embed(title="Welcome Message Added!", description="Here's an example: " + example,
                              colour=discord.Colour.dark_green())

        embed.add_field(name="Channel", value=channel.mention)

        await ctx.send(embed=embed)

    async def checkAndAssignRole(self, role, message: discord.Message):
        member = message.author

        sql = "SELECT `role_id`,`is_admin_only` FROM `discord_role_aliases` WHERE `server_id`=%s AND `alias`=%s"
        cursor = self.database.query(sql, [message.guild.id, role])
        result = cursor.fetchone()

        if not result:
            return

        role = discord.utils.get(message.guild.roles, id=str(result['role_id']))
        await self.client.add_roles(message.author, role)

        with connection.cursor() as cursor:
            sql = "UPDATE `discord_role_aliases` SET `uses`=`uses`+1 WHERE `server_id`=%s AND `role_id`=%s"
            cursor.execute(sql, [message.guild.id, role.id])
            result = cursor.fetchone()

        try:
            with connection.cursor() as cursor:
                sql = "SELECT `overwrite_role_id` FROM `discord_role_overwrites` WHERE `role_id`=%s"
                cursor.execute(sql, [role.id])
                overwrites = cursor.fetchall()
        finally:
            connection.commit()
            connection.close()

        await self.client.delete_message(message)

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(kick_members=True)
    async def names(self, ctx, member: discord.Member):
        """ See the history of name changes the bot has for a person.

        You must have kick members permission to do this."""
        sql = "SELECT `name` FROM `discord_username_changes` WHERE `user_id`=%s"
        cursor = self.database.query(sql, [member.id])
        names = cursor.fetchall()

        msg = ""

        for name in names:
            msg += name['name'] + "\n"

        if ("" == msg):
            msg = "No name changes found."
        else:
            msg = "These are the name changes I have stored: \n" + msg;

        await self.client.send(msg)

    async def findRoleByName(self, role_name, server):
        for role in server.roles:
            if role.name.lower() == role_name.lower():
                return role

        return None

    async def findRoleById(self, id, server):
        for role in server.roles:
            if str(role.id) == str(id):
                return role

        return None

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_messages=True, add_reactions=True)
    async def react(self, ctx, emoji: str, channel: discord.TextChannel, limit=50):
        """ Reacts to messages in the channel. """
        # A quick and dirty way of handling custom emoji.
        if (emoji.startswith("<")):
            emoji = emoji.replace(":", "", 1).replace("<", "").replace(">", "")

        if limit > 100:
            await self.client.send("Discord Bots are only allowed to get 100 messages at a time.")
            return

        get_message = self.client.get_cog("GetMessages")
        data = await get_message.getMessages(channel.id, limit)

        for x in data:
            message = self.client.connection._create_message(channel=channel, **x)
            await self.client.add_reaction(message, emoji)

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_messages=True, add_reactions=True)
    async def clearreacts(self, ctx, channel: discord.TextChannel, emoji: str = None, user: discord.User = None,
                          limit=50):
        """ Clears reactions to messages in the channel.

        If an emoji is provided then it will clear all reactions of a specific emoji. However due to a limitation with Discord it can only remove the messages by the bot, or a provided user."""
        # A quick and dirty way of handling custom emoji.
        if (emoji):
            if (emoji.startswith("<")):
                emoji.replace(":", "").replace("<", "").replace(">", "")

        if limit > 100:
            await self.client.send("Discord Bots are only allowed to get 100 messages at a time.")
            return

        get_message = self.client.get_cog("GetMessages")
        data = await get_message.getMessages(channel.id, limit)

        for x in data:
            message = self.client.connection._create_message(channel=channel, **x)
            if (emoji):
                await self.client.remove_reaction(message, emoji, user if user else self.client.user)
            else:
                await self.client.clear_reactions(message)

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_roles=True)
    async def roleoverwrites(self, ctx, *, role_name):
        """When a role has been assigned a command, any overwrite will remove that role when the command is used.

        If you have roles with the same name the last one will be chosen.
        You must have the "Manage Roles" privilege in order to use this command."""
        server = ctx.message.guild
        assign_role = None
        for role in server.roles:
            if role.name.lower() == role_name.lower():
                assign_role = role

        if assign_role == None:
            await self.client.send("This role could not be found.")
            return

        await self.client.send(
            "Reply with the names of the roles you want to find here. If you want to overwrite more than one, seperate it with a comma.")
        choices = await self.client.wait_for("message", check=lambda m: m.author == message.author)

        choices = choices.content.split(",")
        for role_name in choices:
            chosen_role = await self.findRoleByName(role_name.strip(), server)

            if None == chosen_role or chosen_role == assign_role:
                continue

            sql = "INSERT INTO `discord_role_overwrites` VALUES(0,%s,%s,%s)"
            cursor = self.database.query(sql, [assign_role.id, chosen_role.id, server.id])

        await self.client.send("Done! Roles will be overwritten when they use the command.")

    @commands.command(no_pm=True, hidden=True, pass_context=True)
    @credential_checks.hasPermissions(manage_roles=True)
    async def roleinfo(self, ctx, *, role_name):
        """Get information on a role

        If you have roles with the same name the last one will be chosen.
        You must have the "Manage Roles" privilege in order to use this command."""
        server = ctx.message.guild
        assign_role = None
        for role in server.roles:
            if role.name.lower() == role_name.lower():
                assign_role = role

        if assign_role == None:
            await self.client.send("This role could not be found.")
            return

        sql = "SELECT * FROM `discord_role_aliases` WHERE `server_id`=%s AND `role_id`=%s"
        cursor = self.database.query(sql, [server.id, assign_role.id])
        result = cursor.fetchone()

        total_users = 0
        for member in server.members:
            if assign_role in member.roles:
                total_users = total_users + 1

        embed = discord.Embed(title=assign_role.name, colour=assign_role.colour,
                              description="Role information for \"" + assign_role.name + "\"")
        embed.add_field(name="Members", value=total_users)
        embed.add_field(name="Can be mentioned?", value="Yes" if assign_role.mentionable else "No")
        embed.add_field(name="Created", value=assign_role.created_at.strftime("%d of %b (%Y) %H:%M:%S"))

        if result:
            embed.add_field(name="Command Name", value=result['alias'])
            embed.add_field(name="Command Uses", value=result['uses'])

        await self.client.send_message(ctx.message.channel, embed=embed)

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_roles=True)
    async def rolereact(self, ctx, *, role_name):
        """Adds a role to the bot so that it can be self assigned by reacting to a message.

        Migaga will ask for the message ID and then the reaction, if you have roles with the same name the last one will be chosen.
        You must have the "Manage Roles" privilege in order to use this command."""
        server = ctx.message.guild
        assign_role = None
        for role in server.roles:
            if role.name.lower() == role_name.lower():
                assign_role = role

        if assign_role == None:
            await self.client.send("This role could not be found and therefore could not be registered!")
            return

        await self.client.send("Role found: " + assign_role.name + ", its ID is " + assign_role.id)
        await self.client.send(
            "What is the ID of the message to be reacted to? If you don't know how to get a message ID just say \"help\"!")

        response = await self.client.wait_for("message", check=lambda m: m.author == message.author)

        while (response.content == "help"):
            await self.client.send(
                "Here's a helpful support post about it! https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-")
            response = await self.client.wait_for("message", check=lambda m: m.author == message.author)

        message_id = response.content.strip()

        try:
            message = self.client.get_message(alias)
        except NotFound as e:
            await self.client.send("Sorry that message could not be found!")
        except Forbidden as e:
            await self.client.send("Sorry, I am forbidden to do that!")
        except Exception as e:
            await self.client.send("Sorry, something went wrong. Please try again?")
            raise e

        sql = "SELECT * FROM `discord_role_aliases` WHERE `role_id`=%s"

        cursor = self.database.query(sql, [assign_role.id])
        result = cursor.fetchone()
        if None == result:
            pass
        else:
            await self.client.send(
                "This role already has an alias, it is " + result['alias'] + " this command will override it.")
            database.query("DELETE FROM `discord_role_aliases` WHERE `role_id`=%s", assign_role.id)

        database.query("INSERT INTO `discord_role_aliases` VALUES (0, %s, %s, %s, '0','0');",
                       [alias, assign_role.id, server.id])

        connection.commit()
        await self.client.send(
            "Whew! All done! I have added the role **" + assign_role.name + "**, to the alias: **" + alias + "** in this server: **" + server.name + "**")

    @commands.command(no_pm=True, hidden=True, pass_context=True)
    @credential_checks.hasPermissions(manage_messages=True)
    async def purge(self, ctx, number_of_messages: int):
        """Delete a number of messages from the channel you type it in!"""
        try:
            await self.client.purge_from(ctx.message.channel, limit=number_of_messages + 1)
        except:
            await self.client.send(
                "There was an error deleting. Be aware that Discord does not allow bots to bulk delete messages that are under 14 days old.")


def setup(client):
    client.add_cog(Admin(client))
