import logging
import sys
from datetime import *

import discord
from discord import RawReactionActionEvent
from discord.ext import commands, tasks

from model.model import *
from .utilities import credential_checks

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
        # The cleaner checks all starboard messages in the past week.
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
                embed = await self._get_starred_embed(message_to_check, discord_message, True)
            except:
                # Temporary error handling until discord.py releases 1.4.
                e = sys.exc_info()[0]
                logger.error("Error processing starboard messages: {}".format(e))
                continue

            await self._update_starred_message(message_to_check, embed)
            logger.info("Checked {.message_id}".format(message_to_check))

            # Only check if the message meets the threshold when cleaning up.
            embed = await self._get_starred_embed(message_to_check, discord_message, True)
            await self._update_starred_message(message_to_check, embed)

    @cleaner.before_loop
    async def before_cleaner(self):
        await self.client.wait_until_ready()

    @commands.command(no_pm=True)
    @credential_checks.has_permissions(administrator=True)
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

    @commands.command(no_pm=True, aliases=['threshold'])
    @credential_checks.has_permissions(administrator=True)
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

    async def _get_starred_embed(self, starred_message: StarredMessageModel, discord_message: discord.Message,
                                 remove_after_threshold: bool = False):
        description = "\"{.content}\"".format(discord_message) if discord_message.content else ""
        footer_template = "{} This message doesn't have enough stars to stay in the starboard and will be deleted {}!"

        e = discord.Embed(description=description, colour=discord.Colour.gold())

        author = discord_message.author
        e.set_author(name=author.display_name)
        e.set_thumbnail(url=author.avatar_url)

        if discord_message.attachments:
            e.set_image(url=discord_message.attachments[0].proxy_url)

        number_of_stars = len(starred_message.starrers)
        star_emoji = _get_emoji_for_star(number_of_stars)

        if number_of_stars == 0:
            return

        if number_of_stars < starred_message.starboard.star_threshold:
            if remove_after_threshold:
                return None

            star_emoji = '\N{GHOST}'

            if self.cleaner.next_iteration:
                timer = self.cleaner.next_iteration - datetime.now(timezone.utc)
                countdown = "in {} minutes".format(round(timer.total_seconds() / 60))
            else:
                countdown = "soon"

            e.set_footer(text=footer_template.format(star_emoji, countdown))

        e.add_field(name="Stars", value=star_emoji + " **{}**".format(number_of_stars), inline=True)
        e.add_field(name="Message",
                    value="[Jump to the message]({.jump_url})".format(discord_message),
                    inline=True)

        return e

    async def _on_reaction_removed(self, reaction: RawReactionActionEvent):
        guild_config = await GuildConfig.get_for_guild(reaction.guild_id)
        has_emoji = "⭐" == reaction.emoji.name

        if guild_config.starboard_emoji_id is not None:
            has_emoji = reaction.emoji.id == guild_config.starboard_emoji_id

        if not has_emoji:
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
        guild_config = await GuildConfig.get_for_guild(reaction.guild_id)
        has_emoji = "⭐" == reaction.emoji.name

        if guild_config.starboard_emoji_id is not None:
            has_emoji = reaction.emoji.id == guild_config.starboard_emoji_id

        if not has_emoji:
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

    async def _get_guild_star(self, guild_id: int):
        pass

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
            embed_message = await starboard_channel.fetch_message(starred_message.embed_message_id)

            if embed is not None:
                await embed_message.edit(embed=embed)
                return

            # If the embed can no longer be generated but a message has been posted for it:
            # Remove the embed ID and delete the message.
            starred_message.embed_message_id = None
            starred_message.save()

            return await embed_message.delete()


def setup(client):
    client.add_cog(Starboard(client))
