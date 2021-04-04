import logging
import sys
from datetime import *

import discord
from discord import RawReactionActionEvent, errors
from discord.ext import commands, tasks

from model.embeds import StarboardEmbed
from model.model import *
from discord_slash import cog_ext, SlashContext

logger = logging.getLogger('discord')


def _get_emoji_for_star(stars):
    if 5 >= stars >= 0:
        return '\N{WHITE MEDIUM STAR}'
    elif 10 >= stars >= 6:
        return '\N{GLOWING STAR}'
    elif 25 >= stars >= 11:
        return '\N{DIZZY SYMBOL}'
    else:
        return '\N{SPARKLES}'


class Starboard(commands.Cog):
    """ Commands related to the Starboard. """

    def __init__(self, client: commands.Bot):
        client.add_listener(self._on_reaction, "on_raw_reaction_add")
        client.add_listener(self._on_reaction_removed, "on_raw_reaction_remove")

        self.cleaner.start()
        self.client = client

    def cog_unload(self):
        self.cleaner.cancel()

    @tasks.loop(minutes=5)
    async def cleaner(self):
        threshold = datetime.today() - timedelta(days=1)
        messages_to_check = StarredMessageModel.select().where(StarredMessageModel.datetime_added > threshold)

        # For each message, it updates the embed.
        for message_to_check in messages_to_check:
            channel = self.client.get_channel(message_to_check.message_channel_id)

            # The bot may have been removed from the server.
            if channel is None:
                continue

            try:
                discord_message = await channel.fetch_message(message_to_check.message_id)
                embed = await self._get_starred_embed(message_to_check, discord_message)
            except:
                # Temporary error handling until discord.py releases 1.4.
                e = sys.exc_info()[0]
                logger.error("Error processing starboard messages: {}".format(e))
                continue

            await self._update_starred_message(message_to_check, embed)
            logger.info("Checked {.message_id}".format(message_to_check))

            # Only check if the message meets the threshold when cleaning up.
            embed = await self._get_starred_embed(message_to_check, discord_message)
            await self._update_starred_message(message_to_check, embed)

    @cleaner.before_loop
    async def before_cleaner(self):
        await self.client.wait_until_ready()

    @commands.command(no_pm=True, aliases=['threshold'])
    @commands.has_permissions(administrator=True)
    async def starboardthreshold(self, ctx, threshold: int):
        """
        A command which allows you to set the amount of stars a single message can receive before it makes it into the starboard.

        You must have administrator permissions to perform this.
        """
        starboard = StarboardModel.get_for_guild(ctx.guild.id)

        if starboard is None:
            return await ctx.send(
                "Couldn't find a starboard for this server. Use the `!starboard` command to set one up.")

        if threshold < 0:
            return await ctx.send("You can't have negative stars!")

        starboard.star_threshold = threshold
        starboard.save()

        await ctx.send(
            "Ok! Your starboard's threshold has been set to {}. Messages within the past week will be updated soon.".format(
                threshold))

    async def _get_emoji(self, guild_id):
        guild_config = await GuildConfig.get_for_guild(guild_id)

        if guild_config.starboard_emoji_id is None:
            return "⭐"

        return self.client.get_emoji(guild_config.starboard_emoji_id)

    async def _get_starred_embed(self, starred_message: StarredMessageModel, discord_message: discord.Message):

        number_of_stars = len(starred_message.starrers)
        star_emoji = await self._get_emoji(discord_message.guild.id)

        if number_of_stars == 0:
            return

        e = StarboardEmbed(message=discord_message,
                           starred_message=starred_message,
                           cleaner_next_iteration=self.cleaner.next_iteration,
                           star_emoji=star_emoji)

        return e.populate()

    async def _on_reaction_removed(self, reaction: RawReactionActionEvent):
        guild_emoji = await self._get_emoji(reaction.guild_id)

        if isinstance(guild_emoji, str):
            if reaction.emoji.name != guild_emoji:
                return

        else:
            if reaction.emoji.id != guild_emoji.id:
                return

        starred_message = StarredMessageModel.get_or_none(reaction.message_id)

        if starred_message is None:
            return

        MessageStarrerModel.delete().where((MessageStarrerModel.message_id == reaction.message_id) &
                                           (MessageStarrerModel.user_id == reaction.user_id)).execute()

        channel = self.client.get_channel(starred_message.starboard.channel_id)
        discord_message = await channel.fetch_message(reaction.message_id)

        embed = await self._get_starred_embed(starred_message, discord_message)

        await self._update_starred_message(starred_message, embed)

    async def _on_reaction(self, reaction: RawReactionActionEvent):
        guild_emoji = await self._get_emoji(reaction.guild_id)

        if isinstance(guild_emoji, str):
            if reaction.emoji.name != guild_emoji:
                return

        else:
            if reaction.emoji.id != guild_emoji.id:
                return

        starboard = StarboardModel.get_for_guild(reaction.guild_id)

        if starboard is None:
            return

        channel = self.client.get_channel(reaction.channel_id)
        starred_message = StarredMessageModel.get_or_none(reaction.message_id)
        discord_message = await channel.fetch_message(reaction.message_id)

        if starred_message is None:
            starred_message = StarredMessageModel.create(message_id=discord_message.id,
                                                         message_channel_id=discord_message.channel.id,
                                                         starboard_id=starboard.id,
                                                         is_muted=False, datetime_added=datetime.utcnow(),
                                                         user_id=discord_message.author.id)

        # Don't interact with muted messages or let people star themselves.
        if starred_message.is_muted or discord_message.author.id == reaction.user_id:
            return

        # Add the reactor.
        insert = MessageStarrerModel.insert(message_id=starred_message.message_id, user_id=reaction.user_id,
                                            datetime_starred=datetime.utcnow()) \
            .on_conflict(
            update={MessageStarrerModel.datetime_starred: datetime.utcnow()}) \
            .execute()

        # Show it in the starboard.
        embed = await self._get_starred_embed(starred_message, discord_message)
        await self._update_starred_message(starred_message, embed)

    async def _update_starred_message(self, starred_message: StarredMessageModel,
                                      embed: discord.Embed):

        starboard_channel = self.client.get_channel(starred_message.starboard.channel_id)

        # Either send it (if it hasn't already been submitted to the starboard) or update it.
        if starred_message.embed_message_id is None:
            # If we don't have a message or an embed, continue the logic. We can sort it later.
            if embed is None:
                return

            embed_message = await starboard_channel.send(embed=embed)

            starred_message.embed_message_id = embed_message.id
            starred_message.save()
        else:
            try:
                embed_message = await starboard_channel.fetch_message(starred_message.embed_message_id)
            except errors.NotFound:
                return

            if embed is not None:
                await embed_message.edit(embed=embed)
                return

            # If the embed can no longer be generated but a message has been posted for it:
            # Remove the embed ID and delete the message.
            starred_message.embed_message_id = None
            starred_message.save()

            return await embed_message.delete()

    ### Slash Commands Below
    @cog_ext.cog_subcommand(base="starboard", name="setup",
                            description="Sets up a new starboard for this server in a given channel",
                            guild_ids=[197972184466063381])
    @commands.has_permissions(manage_guild=True)
    async def _setup_starboard(self, ctx: SlashContext, channel: discord.TextChannel, emoji: discord.Emoji):
        if channel is None:
            await ctx.send("You need to provide an existing channel to turn it into a Starboard!")
            return

        args = []
        bot_permissions = ctx.channel.permissions_for(ctx.guild.me)

        # Make sure that people cannot send messages in the starboard.
        if bot_permissions.manage_roles:
            mine = discord.PermissionOverwrite(send_messages=True, manage_messages=True, embed_links=True)
            everyone = discord.PermissionOverwrite(read_messages=True, send_messages=False, read_message_history=True,
                                                   add_reactions=False)
            args.append((ctx.guild.me, mine))
            args.append((ctx.guild.default_role, everyone))
        else:
            await ctx.send("I can't update the channel permissions to stop people talking. Maybe check that?")

        await ctx.send(
            '\N{GLOWING STAR} Starboard set up at {.mention}. Permissions have been updated.'.format(channel))


def setup(client):
    client.add_cog(Starboard(client))
