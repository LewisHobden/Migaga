from datetime import datetime, timezone

import discord
import requests

from model.model import StarredMessageModel


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
        self._remove_after_threshold = kwargs.get("remove_after_threshold", False)
        self._star_emoji = kwargs.get("star_emoji", "⭐")

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

        self.add_field(name="Starred Message", value=content, inline=False)

    def _populate_reply(self):
        """
        If the starred message is in reply to another post, that context should be displayed.
        :return: void
        """
        # If this message is a reply, show a reference to the reply.
        if self._discord_message.reference is None or self._discord_message.reference.resolved is None:
            return

        reply_message = self._discord_message.reference.resolved

        self.add_field(name="Replying to a message by {.display_name}".format(reply_message.author),
                       value="\"{}\"".format(reply_message.clean_content), inline=False)

    def _populate_threshold_check(self, number_of_stars: int):
        """
        If the cleaner intends to remove this message as it is under the threshold, display a notice on the message.
        :param number_of_stars: int
        :return: void
        """
        footer_template = "{} This message doesn't have enough stars to stay in the starboard and will be deleted {}!"

        if self._starred_message.starboard.star_threshold == 1:
            return

        if number_of_stars > self._starred_message.starboard.star_threshold:
            return

        if self._remove_after_threshold:
            return

        star_emoji = '\N{GHOST}'

        if self._cleaner_next_iteration:
            timer = self._cleaner_next_iteration - datetime.now(timezone.utc)
            countdown = "in {} minutes".format(round(timer.total_seconds() / 60))
        else:
            countdown = "soon"

        self.set_footer(text=footer_template.format(star_emoji, countdown))
