from discord import Message
from discord.ext import commands
from discord_slash import cog_ext, SlashCommandOptionType, SlashContext


class MessageEventCog(commands.Cog, name="Message Events"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self._auto_replies = []

        self.client.add_listener(self._on_message, "on_message")

    async def _on_message(self, message: Message):
        for auto_reply in self._auto_replies:
            if auto_reply['strict']:
                if auto_reply['contains'] == message.content:
                    await message.reply(auto_reply['response'])
            else:
                if auto_reply['contains'] in message.content:
                    await message.reply(auto_reply['response'])

    @cog_ext.cog_subcommand(base="message", subcommand_group="events", name="add-auto-reply",
                            description="Adds an auto reply event if a message comes in that contains your criteria!",
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
        self._auto_replies.append(dict(
            guild=ctx.guild.id,
            contains=contains,
            response=response,
            strict=strict
        ))

        await ctx.send("New auto reply has been set up.")


def setup(client):
    client.add_cog(MessageEventCog(client))
