import logging
from typing import List

import discord
from discord import Message, Guild
from discord.ext import commands, tasks
from discord_slash import cog_ext, SlashCommandOptionType, SlashContext
from peewee import DoesNotExist

from model.model import MessageEvent

logger = logging.getLogger('discord')


class MessageEventEmbed(discord.Embed):
    def __init__(self, event: MessageEvent, **kwargs):
        kwargs['colour'] = discord.Colour.dark_orange() if event.response else discord.Colour.magenta()
        kwargs['description'] = "{} messages {} \"{}\".".format("Deletes" if event.response is None else "Replies to",
                                                                "saying" if event.is_strict else "including",
                                                                event.contains)

        if event.response is not None:
            kwargs['description'] += "\n\nSaying \"{}\"".format(event.response)

        super().__init__(**kwargs)

        self.add_field(name="Strict?", value="Yes" if event.is_strict else "No")
        self.add_field(name="Reference", value=event.reference)


class MessageMatchingController:
    def __init__(self, to_match: str, strict: bool):
        self._to_match = to_match.lower()
        self._strict = strict

    def check_match(self, pattern):
        pattern = self._cleanse_pattern(pattern)

        if self._strict:
            return self._to_match == pattern

        return self._to_match in pattern

    def _cleanse_pattern(self, pattern: str):
        """ Helps to remove common exploits by providing the input as cleanly as possible. """
        # Substitute known characters?
        pattern = discord.utils.remove_markdown(pattern)

        return pattern.lower()


class MessageEventCog(commands.Cog, name="Message Events"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self._events = dict()

        self.client.add_listener(self._on_message, "on_message")
        self._cache_events.start()

    def cog_unload(self):
        self._cache_events.cancel()

    @tasks.loop(minutes=30)
    async def _cache_events(self):
        logger.info("Updating message event cache...")
        self._events = dict()

        for event in MessageEvent.select():
            self.add_event(event)

    async def _on_message(self, message: Message):
        # Ignore ourselves, bots, etc.
        if message.author.bot:
            return

        for event in self.get_events(message.guild):
            controller = MessageMatchingController(event.contains, event.is_strict)

            if not controller.check_match(message.clean_content):
                continue

            if event.response is None:
                await message.delete()
            else:
                await message.reply(event.response)

    @cog_ext.cog_subcommand(base="message", subcommand_group="event", name="delete",
                            description="Deletes a message event from your guild.",
                            guild_ids=[197972184466063381],
                            options=[{"name": "reference", "description": "The reference of the message to delete.",
                                      "type": SlashCommandOptionType.STRING, "required": True}])
    @commands.has_permissions(manage_guild=True)
    async def _delete_event(self, ctx: SlashContext, reference: str):
        try:
            stored_event = MessageEvent.get_by_id(reference)
        except DoesNotExist:
            return await ctx.send("A message could not be found for that ID. Try using the list command?")

        stored_event.delete_instance()

        await ctx.send("Message was deleted successfully!")
        await self._cache_events()

    @cog_ext.cog_subcommand(base="message", subcommand_group="event", name="list",
                            description="Lists all message events in your guild.",
                            guild_ids=[197972184466063381]
                            )
    @commands.has_permissions(manage_guild=True)
    async def _list_events(self, ctx: SlashContext):
        for event in MessageEvent.get_for_guild(ctx.guild.id):
            await ctx.send(embed=MessageEventEmbed(event, title="Message Event"))

    @cog_ext.cog_subcommand(base="message", subcommand_group="event", name="add-auto-delete",
                            description="Adds an auto reply event if a message comes in that contains your criteria!",
                            guild_ids=[197972184466063381],
                            options=[dict(name="contains",
                                          description="The content the message may contain to trigger a response.",
                                          type=SlashCommandOptionType.STRING, required=True),
                                     dict(name="strict",
                                          description="If strict, the reply will only come through if the message has "
                                                      "no other text in it.",
                                          type=SlashCommandOptionType.BOOLEAN, required=True)])
    @commands.has_permissions(manage_guild=True)
    async def _setup_auto_delete(self, ctx: SlashContext, contains: str, strict: bool):
        event = MessageEvent.add_for_guild(
            guild=ctx.guild,
            contains=contains,
            response=None,
            is_strict=strict
        )

        await ctx.send(embed=MessageEventEmbed(event, title="New Auto Delete Enabled!"))

        self.add_event(event)

    @cog_ext.cog_subcommand(base="message", subcommand_group="event", name="add-auto-reply",
                            description="Adds an auto delete event if a message comes in that contains your criteria!",
                            guild_ids=[197972184466063381],
                            options=[dict(name="contains",
                                          description="The content the message may contain to trigger a response.",
                                          type=SlashCommandOptionType.STRING, required=True),
                                     dict(name="response",
                                          description="What the bot should reply with.",
                                          type=SlashCommandOptionType.STRING, required=True),
                                     dict(name="strict",
                                          description="If strict, the reply will only come through if the message has "
                                                      "no other text in it.",
                                          type=SlashCommandOptionType.BOOLEAN, required=True)])
    @commands.has_permissions(manage_guild=True)
    async def _setup_auto_reply(self, ctx: SlashContext, contains: str, response: str, strict: bool):
        event = MessageEvent.add_for_guild(
            guild=ctx.guild,
            contains=contains,
            response=response,
            is_strict=strict
        )

        await ctx.send(embed=MessageEventEmbed(event, title="New Auto Reply Enabled!"))
        self.add_event(event)

    def get_events(self, guild: Guild) -> List[MessageEvent]:
        if guild.id not in self._events:
            return []

        return self._events[guild.id]

    def add_event(self, event: MessageEvent):
        gid = event.guild_id

        if gid in self._events:
            self._events[gid].append(event)
        else:
            self._events[gid] = [event]


def setup(client):
    client.add_cog(MessageEventCog(client))
