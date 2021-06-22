import json

import discord
from discord import Message, utils
from discord.ext import commands
from discord_slash import cog_ext, SlashCommandOptionType, SlashContext


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
        self._auto_replies = []
        self._auto_deletes = []

        self.client.add_listener(self._on_message, "on_message")

    async def _on_message(self, message: Message):
        # Ignore ourselves, bots, etc.
        if message.author.bot:
            return

        for auto_delete in self._auto_deletes:
            controller = MessageMatchingController(auto_delete['contains'], auto_delete['strict'])

            if controller.check_match(message.clean_content):
                await message.delete()

        for auto_reply in self._auto_replies:
            controller = MessageMatchingController(auto_reply['contains'], auto_reply['strict'])

            if controller.check_match(message.clean_content):
                await message.reply(auto_reply['response'])

    @cog_ext.cog_subcommand(base="message", subcommand_group="events", name="add-auto-delete",
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
        data = dict(
            guild=ctx.guild.id,
            contains=contains,
            strict=strict
        )

        self._auto_deletes.append(data)

        await ctx.send("New auto delete has been set up {}.".format(json.dumps(data)))

    @cog_ext.cog_subcommand(base="message", subcommand_group="events", name="add-auto-reply",
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
        data = dict(
            guild=ctx.guild.id,
            contains=contains,
            response=response,
            strict=strict
        )

        self._auto_replies.append(data)

        await ctx.send("New auto reply has been set up {}.".format(json.dumps(data)))


def setup(client):
    client.add_cog(MessageEventCog(client))
