from discord.ext import commands
import discord
from cogs.utilities import credential_checks
from model.role_alias import RoleAlias
from model.role_overwrite import RoleOverwrite
from model.welcome_message import WelcomeMessage
import logging

log = logging.getLogger(__name__)


class Admin(commands.Cog):
    """Moderation related commands."""

    def __init__(self, client: commands.Bot):
        self.client = client
        client.add_listener(self._on_member_join, "on_member_join")

    @commands.command()
    async def invite(self, ctx):
        """ Get a URL to invite the bot to your own server! """
        await ctx.send(discord.utils.oauth_url(self.client.client_id))

    @commands.command(no_pm=True, )
    @credential_checks.has_permissions(ban_members=True)
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

    @commands.command(no_pm=True, )
    @credential_checks.has_permissions(ban_members=True)
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

    @commands.command(no_pm=True, )
    @credential_checks.has_permissions(kick_members=True)
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

    @commands.command(no_pm=True, )
    @credential_checks.has_permissions(manage_roles=True)
    async def unflaired(self, ctx):
        """ Counts the total number of people without flairs in the server.

        You must have "Manage Roles" in order to run this command."""
        unflaired_users = []
        for member in ctx.message.guild.members:
            if len(member.roles) == 1:
                unflaired_users.append(member)

        plural = "people" if len(unflaired_users) > 1 else "person"
        await ctx.send("I found " + str(len(unflaired_users)) + " " + plural + " without a role in this server.\n")

    @commands.command(no_pm=True, )
    @credential_checks.has_permissions(ban_members=True)
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

    @commands.command(no_pm=True, )
    @credential_checks.has_permissions(manage_roles=True)
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

    @commands.command()
    @credential_checks.has_permissions(manage_guild=True)
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

    @commands.command(no_pm=True)
    @credential_checks.has_permissions(manage_roles=True)
    async def overwrite(self, ctx, *, role: discord.Role):
        """When a role has been assigned a command, any overwrite will remove that role when the command is used.

        If you have roles with the same name the last one will be chosen.
        You must have the "Manage Roles" privilege in order to use this command."""
        guild = ctx.message.guild

        await ctx.send(
            "Reply with the names of the roles you want to find here. If you want to overwrite more than one, "
            "separate them with a comma.")

        choices = await self.client.wait_for(
            "message", check=lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel)

        choices = choices.content.split(",")
        for role_name in choices:
            try:
                chosen_role = await commands.RoleConverter().convert(ctx, role_name.strip())
            except commands.BadArgument:
                await ctx.send("The role "+role_name+" could not be found and was not added.")
                continue

            RoleOverwrite.create(role_id=role.id, overwrite_role_id=chosen_role.id, server_id=guild.id)

        await ctx.send("Done! Roles will be overwritten when they use the command.")

    @commands.command(no_pm=True, hidden=True, )
    @credential_checks.has_permissions(manage_roles=True)
    async def roleinfo(self, ctx, *, role: discord.Role):
        """Get information on a role.

        If you have roles with the same name the last one will be chosen.
        You must have the "Manage Roles" privilege in order to use this command."""
        guild = ctx.message.guild

        aliases = RoleAlias.select(RoleAlias.alias, RoleAlias.uses)\
            .where(RoleAlias.server_id == ctx.guild.id and RoleAlias.role_id == role.id)

        overwrites = RoleOverwrite.select(RoleOverwrite.overwrite_role_id) \
            .where(RoleOverwrite.server_id == ctx.guild.id and RoleOverwrite.role_id == role.id)

        total_users = 0
        for member in guild.members:
            if role in member.roles:
                total_users = total_users + 1

        embed = discord.Embed(title=role.name, colour=role.colour,
                              description="Role information for \"" + role.name + "\"")

        embed.add_field(name="Members", value=total_users)
        embed.add_field(name="Can be mentioned?", value="Yes" if role.mentionable else "No")
        embed.add_field(name="Created", value=role.created_at.strftime("%d of %b (%Y) %H:%M:%S"))

        for alias in aliases:
            embed.add_field(name="Command Name", value=alias.alias)
            embed.add_field(name="Command Uses", value=alias.uses)

        formatted_overwrites = []
        for overwrite in overwrites:
            formatted_overwrites.append(discord.utils.get(ctx.guild.roles, id=overwrite.overwrite_role_id).name)

        if formatted_overwrites:
            embed.add_field(name="This command overwrites", value=", ".join(formatted_overwrites))

        await ctx.send(embed=embed)

    @commands.command(no_pm=True, hidden=True, )
    @credential_checks.has_permissions(manage_messages=True)
    async def purge(self, ctx, number_of_messages: int, channel: discord.TextChannel = None):
        """Delete a number of messages from the channel you type it in!
        Messages cannot be purged if they are older than 14 days.

        You must have manage messages permission to use this command."""

        if channel is None:
            channel = ctx.channel

        try:
            await channel.purge(limit=number_of_messages + 1)
        except discord.Forbidden:
            await ctx.send("I don't have permission to do this!")
        except discord.HTTPException:
            await ctx.send("I was unable to purge these messages. Are any of them older than 14 days?")

    async def _on_member_join(self, member: discord.Member):
        welcome_messages = WelcomeMessage.select().where(WelcomeMessage.server_id == member.guild.id)

        for message in welcome_messages:
            channel = self.client.get_channel(message.channel_id)
            await channel.send(message.message.format(member.mention, member.display_name, member.guild.name))


def setup(client):
    client.add_cog(Admin(client))
