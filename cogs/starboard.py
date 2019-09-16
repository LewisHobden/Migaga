from datetime import *

from discord import RawReactionActionEvent

from storage.database_factory import DatabaseFactory

import discord
from discord.ext import commands

from model.message_starrer import MessageStarrerModel
from model.starboard import StarboardModel
from model.starred_message import StarredMessageModel
from .utilities import credential_checks


async def _get_emoji_for_star(stars):
    if 5 >= stars >= 0:
        return '\N{WHITE MEDIUM STAR}'
    elif 10 >= stars >= 6:
        return '\N{GLOWING STAR}'
    elif 25 >= stars >= 11:
        return '\N{DIZZY SYMBOL}'
    else:
        return '\N{SPARKLES}'


async def _get_starred_embed(starred_message: StarredMessageModel, discord_message: discord.Message):
    e = discord.Embed(description=discord_message.content, timestamp=discord_message.created_at,colour=discord.Colour.gold())

    author = discord_message.author
    e.set_author(name=author.display_name)
    e.set_thumbnail(url=author.avatar_url)

    if discord_message.attachments:
        e.set_image(url=discord_message.attachments[0].proxy_url)

    number_of_stars = 0
    starrers = starred_message.starrers

    for starrer in starrers:
        # @todo Check if they are blacklisted..
        number_of_stars += 1

    star_emoji = await _get_emoji_for_star(number_of_stars)
    e.add_field(name="Stars", value=star_emoji + " **" + str(number_of_stars) + "**", inline=False)

    return e


class Starboard(commands.Cog):
    """ Commands related to the Starboard. """

    def __init__(self, client: commands.Bot):
        client.add_listener(self._on_reaction, "on_raw_reaction_add")
        client.add_listener(self._on_reaction_removed, "raw_reaction_remove")
        self.client = client

    @commands.command(no_pm=True)
    @credential_checks.hasPermissions(administrator=True)
    async def starboard(self, ctx, *, channel: discord.TextChannel = None):
        """Sets up the starboard for this server.
        This creates a starboard in the specified channel
        this makes it into the server's "starboard".

        If the channel is deleted then the starboard is
        deleted as well.

        You must have Administrator permissions to use this
        command.
        """

        if channel is None:
            ctx.send("You need to provide an existing channel to turn it into a Starboard!")
            return

        # Check the database for a starboard.
        previous_starboard = StarboardModel.get_for_guild(channel.guild.id)

        if previous_starboard is not None:
            # Then check if the channel still exists.
            previous_channel = self.client.get_channel(previous_starboard.channel_id)
            if previous_channel is not None:
                fail_message = 'This server already has a starboard ({.mention})'
                await ctx.send(fail_message.format(previous_channel))
                return
            else:
                clear_message = "This server already _had_ a starboard. I notice it no longer exists or I can't get " \
                                "it. I will delete the old record."

                await ctx.send(clear_message)
                previous_starboard.delete_instance()

        bot_permissions = ctx.message.channel.permissions_for(ctx.guild.me)
        await ctx.send("Updating permissions for {.mention}".format(channel))

        args = []

        # Make sure that people cannot send messages in the starboard.
        if bot_permissions.manage_roles:
            mine = discord.PermissionOverwrite(send_messages=True, manage_messages=True, embed_links=True)
            everyone = discord.PermissionOverwrite(read_messages=True, send_messages=False, read_message_history=True,
                                                   add_reactions=False)
            args.append((ctx.guild.me, mine))
            args.append((ctx.guild.default_role, everyone))
        else:
            await ctx.send("I can't update the channel permissions to stop people talking. Maybe check that?")

        StarboardModel.create(guild_id=ctx.guild.id, channel_id=channel.id, is_locked=False)
        await ctx.send('\N{GLOWING STAR} Starboard set up at {.mention}'.format(channel))

    async def _on_reaction_removed(self, reaction: RawReactionActionEvent):
        # @todo Allow customisation of the emoji for starring.
        if reaction.emoji.name != '⭐':
            return

        starred_message = StarredMessageModel.get_or_none(reaction.message_id)

        if starred_message is None:
            return

        MessageStarrerModel.delete().where((MessageStarrerModel.message_id == reaction.message_id) &
                                           (MessageStarrerModel.user_id == reaction.user_id)).execute()

        channel = self.client.get_channel(reaction.channel_id)
        discord_message = await channel.fetch_message(reaction.message_id)

        embed = await _get_starred_embed(starred_message, discord_message)
        channel = self.client.get_channel(starred_message.starboard.channel_id)

        embed_message = await channel.fetch_message(starred_message.embed_message_id)
        await embed_message.edit(embed=embed)

    async def _on_reaction(self, reaction: RawReactionActionEvent):
        # @todo Allow customisation of the emoji for starring.
        if reaction.emoji.name != '⭐':
            return

        starboard = StarboardModel.get_for_guild(reaction.guild_id)

        if starboard is None:
            return

        channel = self.client.get_channel(reaction.channel_id)
        starred_message = StarredMessageModel.get_or_none(reaction.message_id)
        discord_message = await channel.fetch_message(reaction.message_id)

        if starred_message is None:
            starred_message = StarredMessageModel.create(message_id=discord_message.id, starboard_id=starboard.id,
                                                         is_muted=False, datetime_added=datetime.utcnow(),
                                                         user_id=discord_message.author.id)

        # Don't interact with muted messages or let people star themselves.
        if starred_message.is_muted or discord_message.author.id == reaction.user_id:
            return

        # Add the reactor.
        insert = MessageStarrerModel.insert(message_id=starred_message.message_id, user_id=reaction.user_id,
                                   datetime_starred=datetime.utcnow()) \
            .on_conflict(
            update={MessageStarrerModel.datetime_starred: datetime.utcnow()})\
            .execute()

        # Show it in the starboard.
        embed = await _get_starred_embed(starred_message, discord_message)
        starboard_channel = self.client.get_channel(starboard.channel_id)

        # Either send it (if it hasn't already been submitted to the starboard) or update it.
        if starred_message.embed_message_id is None:
            embed_message = await starboard_channel.send("In {.mention}".format(channel), embed=embed)

            starred_message.embed_message_id = embed_message.id
            starred_message.save()
        else:
            embed_message = await starboard_channel.fetch_message(starred_message.embed_message_id)
            await embed_message.edit(embed=embed)


def setup(client):
    client.add_cog(Starboard(client))
