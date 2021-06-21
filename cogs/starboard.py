import logging
from datetime import *

from discord import RawReactionActionEvent
from discord.ext import commands, tasks
from discord.ext.commands import PartialEmojiConversionFailure
from discord_slash import cog_ext, SlashContext, SlashCommandOptionType

from converters.converters import PartialEmojiWithUnicodeConverter
from model.embeds import StarboardEmbed
from model.model import *

logger = logging.getLogger('discord')


async def _delete_starred_message(message_to_delete: StarredMessageModel, starboard_message: discord.Message):
    message_to_delete.embed_message_id = None
    message_to_delete.save()

    if starboard_message is not None:
        await starboard_message.delete()


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
        """ A process which runs every 5 minutes to ensure all messages are removed if necessary. """
        cleaning_threshold = datetime.today() - timedelta(days=1)
        messages_to_check = StarredMessageModel.select().where(StarredMessageModel.datetime_added > cleaning_threshold)

        logger.info("Running the cleaner for {} starboard message(s).".format(len(messages_to_check)))

        # For each message, it updates the embed.
        for message_to_check in messages_to_check:
            try:
                original_message_channel = self.client.get_channel(message_to_check.message_channel_id)
                starboard_channel = self.client.get_channel(message_to_check.starboard.channel_id)
                starboard_message = None

                # The bot may have been removed from the server, in which case skip it for now.
                if original_message_channel is None:
                    continue

                try:
                    original_message = await original_message_channel.fetch_message(message_to_check.message_id)
                    new_embed = await self._get_starred_embed(message_to_check, original_message)
                except discord.NotFound:
                    new_embed = None

                if message_to_check.embed_message_id:
                    try:
                        starboard_message = await starboard_channel.fetch_message(message_to_check.embed_message_id)
                    except discord.NotFound:
                        continue

                star_threshold = message_to_check.starboard.star_threshold
                number_of_stars = len(message_to_check.starrers)

                if message_to_check.starboard.star_threshold != 1 and number_of_stars < star_threshold:
                    await _delete_starred_message(message_to_check, starboard_message)
                else:
                    await self._update_starred_message(message_to_check, new_embed)
            except Exception as e:
                # For debug purposes, temporarily widening error handling to find Webhook errors.
                logger.error("[{}] There was an error running the starboard: {}".format(message_to_check.message_id, e))

    @cleaner.before_loop
    async def before_cleaner(self):
        await self.client.wait_until_ready()

    async def _get_starred_embed(self, starred_message: StarredMessageModel, discord_message: discord.Message):
        """ Gets an embed when provided with a starred message and the message that should be embedded. """
        # Check the number of stars, if the message has zero stars then we no longer render it.
        number_of_stars = len(starred_message.starrers)
        star_emoji = starred_message.starboard.emoji

        if number_of_stars == 0:
            return

        # Otherwise return a stylised embed for the message.
        e = StarboardEmbed(message=discord_message,
                           starred_message=starred_message,
                           cleaner_next_iteration=self.cleaner.next_iteration,
                           star_emoji=star_emoji)

        return e.populate()

    async def _on_reaction_removed(self, reaction: RawReactionActionEvent):
        starboard = StarboardModel.get_for_guild(reaction.guild_id, reaction.emoji)

        if starboard is None:
            return

        starred_message = await StarredMessageModel.get_in_starboard(reaction.message_id, starboard.id)

        if starred_message is None:
            return

        await MessageStarrerModel.delete_starrer_message(message_id=starred_message.id, starrer_id=reaction.user_id)

        message_channel = self.client.get_channel(reaction.channel_id)
        unstarred_message = await message_channel.fetch_message(reaction.message_id)

        new_embed = await self._get_starred_embed(starred_message, unstarred_message)

        await self._update_starred_message(starred_message, new_embed)

    async def _on_reaction(self, reaction: RawReactionActionEvent):
        starboard = StarboardModel.get_for_guild(reaction.guild_id, reaction.emoji)

        if starboard is None:
            return

        channel = self.client.get_channel(reaction.channel_id)
        starred_message = await StarredMessageModel.get_in_starboard(reaction.message_id, starboard.id)
        discord_message = await channel.fetch_message(reaction.message_id)

        # Users cannot star their own message.
        if discord_message.author.id == reaction.user_id:
            return

        if starred_message is None:
            starred_message = await StarredMessageModel.create_from_message(message=discord_message, starboard=starboard)

        if starred_message.is_muted:
            return

        await MessageStarrerModel.add_starred_message(message_id=starred_message.id, starrer_id=reaction.user_id)

        # Show it in the starboard.
        embed = await self._get_starred_embed(starred_message, discord_message)
        await self._update_starred_message(starred_message, embed)

    async def _update_starred_message(self, starred_message: StarredMessageModel, new_embed: discord.Embed):
        """ Updates a starred message in Discord.
        If the embed provided is None then it attempts to delete the message. """

        starboard_channel = self.client.get_channel(starred_message.starboard.channel_id)

        # If this is the first time submitting this embed, post a new message for it.
        if starred_message.embed_message_id is None and new_embed is not None:
            embed_message = await starboard_channel.send(embed=new_embed)

            starred_message.embed_message_id = embed_message.id
            starred_message.save()

            return

        # Otherwise, we look for the message we posted previously and attempt to update it.
        try:
            original_message = await starboard_channel.fetch_message(starred_message.embed_message_id)
        except (discord.NotFound, discord.HTTPException):
            return

        # If we have been provided an empty embed then it needs deleting.
        if new_embed is None:
            return await _delete_starred_message(starred_message, original_message)

        # Finally, render the new embed.
        await original_message.edit(embed=new_embed)

    @cog_ext.cog_subcommand(base="starboard", name="setup",
                            description="Sets up a starboard for a given channel - updates it if there already is one in the channel.",
                            options=[{"name": "channel", "description": "The channel to set the class up in.", "type": SlashCommandOptionType.CHANNEL, "required": True},
                                     {"name": "emoji", "description": "The emoji for the starboard to use.", "type": SlashCommandOptionType.STRING, "required": True},
                                     {"name": "threshold", "description": "If a message has under these many stars, it will be automatically deleted.", "type": SlashCommandOptionType.INTEGER}])
    @commands.has_permissions(manage_guild=True)
    async def _setup_starboard(self, ctx: SlashContext, channel: discord.TextChannel, emoji: str, threshold: int = 1):
        if not isinstance(channel, discord.TextChannel):
            return await ctx.send("The channel you have provided is not supported.")

        emoji_converter = PartialEmojiWithUnicodeConverter()

        try:
            emoji = await emoji_converter.convert(ctx, emoji)
        except PartialEmojiConversionFailure:
            return await ctx.send("Unknown emoji: {}".format(emoji))

        if emoji not in ctx.guild.emojis and not isinstance(emoji, str):
            await ctx.send("Warning, the emoji you have picked doesn't exist in this server. It could be deleted "
                           "without your knowledge!")

        StarboardModel.add_or_update(ctx.guild.id, channel.id, str(emoji), threshold)

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

        await ctx.send('{} Starboard set up at {.mention}. Permissions have been updated.'.format(emoji, channel))


def setup(client):
    client.add_cog(Starboard(client))
