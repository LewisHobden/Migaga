from datetime import datetime, timezone

import discord
import requests
from discord import Guild
from emoji import emojize

from cogs.utilities.formatting import format_points
from model.model import StarredMessageModel, GuildConfig, MemberWarning


class ConfigEmbed(discord.Embed):
    def __init__(self, guild_config: GuildConfig, **kwargs):
        super().__init__(**kwargs, color=discord.Color.blue(), title="Your Config",
                         description="These are all the config settings for your server.")

        logs_channel = "Not Enabled"

        if guild_config.server_logs_channel_id is not None:
            logs_channel = "<#{}>".format(guild_config.server_logs_channel_id)

        points_emoji = "*Not Setup*"
        if guild_config.points_emoji is not None:
            points_emoji = guild_config.points_emoji

        self.add_field(name="Server Logs", value=logs_channel)
        self.add_field(name="Points", value=guild_config.points_name if not None else "*Not Setup*")
        self.add_field(name="Points Emoji", value=points_emoji)


class LeaderboardEmbed(discord.Embed):
    def __init__(self, config: GuildConfig, guild: Guild, **kwargs):
        self.entries = []

        points = config.points_name[0].upper()
        points += config.points_name[1:]

        super().__init__(**kwargs, title="{} Leaderboard for {}".format(points, guild.name))

    def add_entry(self, position: int, item: str, total: float):
        if 1 == position:
            position = emojize(":star: {}".format(position))

        self.entries.append("{}. **{}** - {}".format(position, item, format_points(total)))

    def populate(self):
        self.description = "\n".join(self.entries)
        return self


class StarboardEmbed(discord.Embed):
    """An embed for a message being posted to the Starboard.

       Attributes
       -----------
       cleaner_next_iteration: :class:`datetime`
           The datetime that starboard messages will next be cleaned up. Can be None.
       star_emoji: :class:`str`
           The custom, or regular emoji to represent stars on the starboard.
       remove_after_threshold: :class:`bool`
           Whether or not a starboard message will be removed if under the threshold.
       """
    def __init__(self, message: discord.Message, starred_message: StarredMessageModel, **kwargs):
        self._cleaner_next_iteration = kwargs.get("cleaner_next_iteration")
        self._discord_message = message
        self._starred_message = starred_message
        self._star_emoji = kwargs.get("star_emoji", "⭐")

        kwargs['title'] = "Starred Message"
        kwargs['colour'] = discord.Colour.gold()
        super().__init__(**kwargs)

    def populate(self):
        """
        Tells the embed to populate itself based on the provided data.
        :return: self
        """
        number_of_stars = len(self._starred_message.starrers)

        self._populate_author()
        self._populate_attachments()
        self._populate_reply()
        self._populate_description()
        self._populate_threshold_check(number_of_stars)

        self.add_field(name="Awards", value="{} **{}**".format(self._star_emoji, number_of_stars), inline=True)

        jump_link = "[Jump to the message]({.jump_url})".format(self._discord_message)
        self.add_field(name="Message", value=jump_link, inline=True)

        return self

    def _populate_attachments(self):
        """
        If the original message had an attachment, attach it to the Embed if Discord supports it.
        :return: void
        """
        if not self._discord_message.attachments:
            return

        # Currently we only use the first attachment in the message.
        attachment = self._discord_message.attachments[0]

        # Trust Discord as the source of truth for metadata, make a request for their Content-Type header.
        content_type = requests.head(attachment.url, stream=True).headers['Content-Type']

        # Once videos are supported in embeds we'll be ready.
        # if content_type.startswith("video/"):
        #     self._video = {"url": attachment.url}

        if content_type.startswith("image/"):
            self.set_image(url=attachment.proxy_url)

    def _populate_author(self):
        """
        The author of the original message should be prominent at the top of the starred message.
        :return: void
        """
        author = self._discord_message.author

        self.set_author(name=author.display_name)
        self.set_thumbnail(url=author.avatar_url)

    def _populate_description(self):
        """
        The description of the message should be the content of the message, unless none can be displayed.
        :return: void
        """
        content = "_I can't seem to show this message, jump to it and see for yourself?_"

        if self._discord_message.content:
            content = "\"{}\"".format(self._discord_message.content)

        self.description = content

    def _populate_reply(self):
        """
        If the starred message is in reply to another post, that context should be displayed.
        :return: void
        """
        # If this message is a reply, show a reference to the reply.
        if self._discord_message.reference is None or self._discord_message.reference.resolved is None:
            return

        reply_message = self._discord_message.reference.resolved
        reply_content = reply_message.clean_content

        # Discord limits embed fields to 1024 characters.
        if len(reply_content) > 1024:
            reply_content = reply_content[:1000] + "..."

        self.add_field(name="Replying to a message by {.display_name}".format(reply_message.author),
                       value="\"{}\"".format(reply_content), inline=False)

    def _populate_threshold_check(self, number_of_stars: int):
        """
        If the cleaner intends to remove this message as it is under the threshold, display a notice on the message.
        :param number_of_stars: int
        :return: void
        """
        footer_template = "{} This message doesn't have enough stars to stay in the starboard and will be deleted {}!"

        if self._starred_message.starboard.star_threshold == 1:
            return

        if number_of_stars >= self._starred_message.starboard.star_threshold:
            return

        star_emoji = '\N{GHOST}'

        if self._cleaner_next_iteration:
            timer = self._cleaner_next_iteration - datetime.now(timezone.utc)
            countdown = "in {} minutes".format(round(timer.total_seconds() / 60))
        else:
            countdown = "soon"

        self.set_footer(text=footer_template.format(star_emoji, countdown))


class UserEmbed(discord.Embed):
    def __init__(self, user: discord.User, **kwargs):
        self.set_thumbnail(url=user.avatar_url)
        self.add_field(name="ID", value=user.id)

        super().__init__(title="{.name}#{.discriminator}".format(user, user), **kwargs)


class WarningsEmbed(discord.Embed):
    def __init__(self, member: discord.Member, **kwargs):
        self.set_thumbnail(url=member.avatar_url)

        total = 0

        for warning in MemberWarning.get_for_member(member):
            total += 1
            self.add_field(name="On {}".format(warning.date_time_created), value=warning.reason_for_warning, inline=False)

        self.set_footer(text="Total Warnings: {}".format(total))
        super().__init__(title="Warnings for {.name}".format(member), colour=member.colour, **kwargs)
