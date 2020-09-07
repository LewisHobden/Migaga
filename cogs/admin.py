import logging

import discord
from discord import RawReactionActionEvent
from discord.ext import commands

from cogs.utilities import credential_checks
from model.model import *

log = logging.getLogger(__name__)


async def _get_roles_from_iterable(iterable, guild: discord.Guild):
    roles_to_provide = []
    roles_to_remove = []

    for alias in iterable:
        role = guild.get_role(alias.role_id)

        if role is None:
            continue

        roles_to_provide.append(role)

        overwrites = RoleOverwrite.select().where(RoleOverwrite.role_id == alias.role_id)

        for overwrite in overwrites:
            role = guild.get_role(overwrite.overwrite_role_id)

            if role is None:
                continue

            roles_to_remove.append(role)

    return roles_to_provide, roles_to_remove


def _format_welcome_message(message: str, member: discord.Member):
    return message.format(member.mention, member.display_name, member.guild.name)


async def _send_disappearing_notification(member: discord.Member, channel: discord.TextChannel, roles, prefix: str):
    # Since join doesn't want to play fair.
    formatted_roles = []
    for role in roles:
        formatted_roles.append(str(role))

    # Send a disappearing message letting them know we've given them the roles.
    msg = prefix + "`{}` for that flair!"

    alert = await channel.send(msg.format(member, ", ".join(formatted_roles)))
    await alert.delete(delay=10)


class Admin(commands.Cog):
    """Moderation related commands."""

    def __init__(self, client: commands.Bot):
        self.client = client
        client.add_listener(self._on_member_join, "on_member_join")
        client.add_listener(self._on_message, "on_message")

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
    async def massban(self, ctx, *, users: str):
        """
        Finds and bans people based on a list of user IDs.
        In order to do this, the bot and you must have Ban Member permissions.

        Separate identifiers with a space..
        """
        ids = users.split(" ")

        for id in ids:
            # Do the least expensive check..
            user = self.client.get_user(id)

            if user:
                await self.ban(ctx, user)
                continue

            # If we must, do the expensive API check.
            try:
                user = await self.client.fetch_user(id)
                await self.ban(ctx, user)
            except discord.NotFound:
                await ctx.send("Could not find user by ID {}".format(id))

    @commands.command(no_pm=True, )
    @credential_checks.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User):
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

    @commands.command(no_pm=True, aliases=['rolecommand'])
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

    @commands.command(aliases=["wm"])
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

    @commands.command(aliases=["rmwm", "deletewelcome","removewm"])
    @credential_checks.has_permissions(manage_guild=True)
    async def removewelcomemessage(self, ctx):
        """
        Allows the user to delete a welcome message from the guild.
        You must have "Manage Guild" permissions to do this.
        """
        messages = WelcomeMessage.get_for_guild(ctx.guild.id)

        if len(messages) == 1:
            messages[0].delete_instance()
            await ctx.send("Your welcome message has been removed!")
            return
        elif len(messages) == 0:
            await ctx.send("Your guild has no welcome messages!")
            return

        embed = discord.Embed(title="Pick welcome message to delete",
                              description="Reply with the number of the message you are trying to delete.",
                              colour=discord.Colour.dark_green())
        index = 1
        indexed_messages = {}

        for message in messages:
            preview = "In <#{.channel_id}>: {.message}".format(message, message)
            preview = _format_welcome_message(preview, ctx.author)

            embed.add_field(name="Message #{}".format(index),
                            value=preview)

            indexed_messages[index] = message
            index += 1

        await ctx.send(embed=embed)
        reply = await self.client.wait_for(
            "message", check=lambda m: m.author == ctx.message.author and m.channel == ctx.channel)

        chosen_index = reply.content.strip().replace("#", "")

        if not chosen_index.isnumeric():
            await ctx.send("I'm not sure what you just tried to delete.. Run the command again?")
            return
        else:
            chosen_index = int(chosen_index)

        if chosen_index in indexed_messages:
            indexed_messages[chosen_index].delete_instance()
            await ctx.send("Message has been removed!")
        else:
            await ctx.send("I'm not sure what you just tried to delete.. Run the command again?")

    @commands.command(no_pm=True, aliases=["roleoverwrite", "rolerule"])
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
                await ctx.send("The role " + role_name + " could not be found and was not added.")
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

        aliases = RoleAlias.select(RoleAlias.alias, RoleAlias.uses) \
            .where((RoleAlias.server_id == ctx.guild.id) & (RoleAlias.role_id == role.id))

        overwrites = RoleOverwrite.select(RoleOverwrite.overwrite_role_id) \
            .where((RoleOverwrite.server_id == ctx.guild.id) & (RoleOverwrite.role_id == role.id))

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

    @commands.command(no_pm=True, hidden=True)
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

    async def _on_message(self, message: discord.Message):
        if not message.content.startswith(self.client.command_prefix):
            return

        space_location = message.content.find(" ")
        if space_location == -1:
            command = message.content[1:]
        else:
            command = message.content[1:space_location]

        aliases = RoleAlias.select().where(RoleAlias.server_id == message.guild.id and RoleAlias.alias % command)
        roles_to_provide, roles_to_remove = await _get_roles_from_iterable(aliases, message.guild)

        await message.author.add_roles(*roles_to_provide, reason="Added using the \"{}\" command.".format(command))
        await message.author.remove_roles(*roles_to_remove, reason="Removed using the \"{}\" command.".format(command))

        if len(roles_to_provide) > 0:
            await message.delete(delay=2)

    async def _on_member_join(self, member: discord.Member):
        welcome_messages = WelcomeMessage.get_for_guild(member.guild.id)

        for message in welcome_messages:
            channel = self.client.get_channel(message.channel_id)
            await channel.send(_format_welcome_message(message.message, member))


class FlairMessage(commands.Cog, name="Reaction Flairs"):
    def __init__(self, client: commands.Bot):
        self.client = client
        client.add_listener(self._on_reaction, "on_raw_reaction_add")
        client.add_listener(self._on_reaction_removed, "on_raw_reaction_remove")

    @commands.command(aliases=["rfinfo"])
    @commands.has_permissions(manage_roles=True)
    async def reactionflairinfo(self, ctx, message: discord.Message):
        """ Shows information on all reaction flairs against a given message."""
        flairs = FlairMessageReactionModel.select().where(FlairMessageReactionModel.discord_message_id == message.id)
        embeds = []

        for flair in flairs:
            desc = "[This message]({.jump_url}) is a flair message.\n"
            role = message.guild.get_role(flair.role_id)
            emoji = message.guild.get_role(flair.role_id)

            embed = discord.Embed(
                title="Role flair {}".format(flair.reference),
                description=desc.format(message),
                colour=role.colour
            )

            embed.add_field(name="Reference", value=flair.reference)
            embed.add_field(name="Emoji", value=emoji.name)
            embed.add_field(name="Message ID", value=message.id)
            embed.add_field(name="Role", value=role.name)
            embed.set_footer(
                text="This may also remove roles when the flair is used. Check using the \"roleinfo\" command.")

            embeds.append(embed)
            await ctx.send(embed=embed)

        if len(embeds) < 1:
            await ctx.send("There are no reaction flairs for this message.")
            return

        # Todo send multiple embeds when this is supported.
        # await ctx.send(embed=embed)

    @commands.command(aliases=["rmrf"])
    @commands.has_permissions(manage_roles=True)
    async def removereactionflair(self, ctx, reference):
        """ Deletes a reaction flair from the system.

        You can only delete a reaction flair using its reference created when the reaction flair was set up.
        If you've forgotten it use the rfinfo command. """
        try:
            model = FlairMessageReactionModel.get_by_id(reference)
        except DoesNotExist:
            await ctx.send("Could not find a reaction flair by the reference `{}`. Try the \"rfinfo\" command."
                           .format(reference))
            return

        model.delete_instance()
        await ctx.send("Done! Removed that reaction flair.")

    @commands.command(aliases=["rf"])
    @commands.has_permissions(manage_roles=True)
    async def reactionflair(self, ctx, message: discord.Message, emoji: discord.Emoji, role: discord.Role):
        """ Adds a new flair reaction to a message.

         This will give a role to the person who reacts to the message with this emoji.
         This also respects the "overwrite" command.
         If a user is uses this reaction then it will remove any roles that have been configured with that command."""
        await message.add_reaction(emoji)

        desc = "[This message]({.jump_url}) has been set up as a flair message.\n"

        model = FlairMessageReactionModel.create(reference=FlairMessageReactionModel.generate_unique_reference(),
                                                 discord_message_id=message.id,
                                                 emoji_id=emoji.id,
                                                 role_id=role.id)

        embed = discord.Embed(
            title="Role flair added!",
            description=desc.format(message),
            colour=role.colour
        )

        embed.add_field(name="Reference", value=model.reference)
        embed.add_field(name="Emoji", value=emoji.name)
        embed.add_field(name="Message ID", value=message.id)
        embed.add_field(name="Role", value=role.name)
        embed.set_footer(
            text="This may also remove roles when the flair is used. Check using the \"roleinfo\" command.")

        await ctx.send(embed=embed)

    async def _on_reaction_removed(self, reaction: RawReactionActionEvent):
        reactions = FlairMessageReactionModel.select().where(
            (FlairMessageReactionModel.discord_message_id == reaction.message_id) &
            (FlairMessageReactionModel.emoji_id == reaction.emoji.id))

        channel = self.client.get_channel(reaction.channel_id)
        guild = channel.guild
        member = channel.guild.get_member(reaction.user_id)
        roles_to_remove = []

        for to_remove in reactions:
            role = guild.get_role(to_remove.role_id)

            if role is None:
                continue

            roles_to_remove.append(role)

        if 0 == len(roles_to_remove):
            return

        await member.remove_roles(*roles_to_remove,
                                  reason="Removed using the \"{}\" reaction.".format(reaction.emoji.name))

        await _send_disappearing_notification(
            member, channel, roles_to_remove, "{.mention}, I have removed the role(s) ")

    async def _on_reaction(self, reaction: RawReactionActionEvent):
        reactions = FlairMessageReactionModel.select().where(
            (FlairMessageReactionModel.discord_message_id == reaction.message_id) &
            (FlairMessageReactionModel.emoji_id == reaction.emoji.id))

        channel = self.client.get_channel(reaction.channel_id)

        roles_to_provide, roles_to_remove = await _get_roles_from_iterable(reactions, channel.guild)
        member = channel.guild.get_member(reaction.user_id)
        emoji_name = reaction.emoji.name

        if 0 == len(roles_to_provide):
            return

        await member.add_roles(*roles_to_provide, reason="Added using the \"{}\" reaction.".format(emoji_name))
        await member.remove_roles(*roles_to_remove, reason="Removed using the \"{}\" reaction.".format(emoji_name))

        await _send_disappearing_notification(
            member, channel, roles_to_provide, "{.mention}, I have given you the role(s) ")


def setup(client):
    client.add_cog(Admin(client))
    client.add_cog(FlairMessage(client))
