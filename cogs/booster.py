import datetime
import discord
from datetime import datetime
from discord import TextChannel, Member
from discord.ext import commands
from discord_slash import cog_ext, SlashCommandOptionType, SlashContext

from model.model import BoosterMessage


class BoosterMessageController:
    def __init__(self, message: str):
        self.message = message

    def format_message(self, member: discord.Member) -> str:
        parsable_message = self.message.replace("<@>", "{0}").replace("<>", "{1}").replace("<s>", "{2}")

        return parsable_message.format(member.mention, member.display_name, member.guild.name)

    async def send_boost_message(self, destination: TextChannel, booster: discord.Member):
        await destination.send(self.format_message(booster))


class NitroBooster(commands.Cog):
    def __init__(self, client: commands.Bot):
        client.add_listener(self._on_member_updated, "on_member_update")
        self.client = client

    async def _on_member_updated(self, member_before: Member, member_after: Member, force=False):
        if force or not (member_before.premium_since is None and member_after.premium_since is not None):
            return

        boost_messages = BoosterMessage.get_for_guild(member_after.guild)

        if not boost_messages:
            return

        for boost_message in boost_messages:
            try:
                destination = self.client.get_channel(boost_message.channel_id)
            except discord.NotFound:
                continue  # Should we delete the message from the database?

            controller = BoosterMessageController(boost_message)
            await controller.send_boost_message(destination, member_after)

    @cog_ext.cog_subcommand(base="booster", subcommand_group="notification", name="add",
                            description="Sets up a new message for when somebody boosts the server.",
                            guild_ids=[750683930549551164],
                            options=[{"name": "channel", "description": "The channel to post the message in.",
                                      "type": SlashCommandOptionType.CHANNEL, "required": True},
                                     {"name": "message",
                                      "description": "The message to post. You can use placeholders!",
                                      "type": SlashCommandOptionType.STRING, "required": True}])
    @commands.has_permissions(manage_guild=True)
    async def _setup_message(self, ctx: SlashContext, channel: TextChannel, message: str):
        if not isinstance(channel, discord.TextChannel):
            return await ctx.send("That channel type isn't supported!")

        db_message = BoosterMessage.add_for_guild(ctx.guild_id, channel, message)
        controller = BoosterMessageController(db_message.message)

        embed = discord.Embed(colour=discord.Colour.purple(),
                              title="New Booster Message Added!",
                              description=controller.format_message(ctx.author),
                              timestamp=datetime.utcnow())

        embed.add_field(name="Channel", value=channel.mention)
        embed.add_field(name="Reference", value=db_message.reference)

        embed.set_footer(text="The \"reference\" is used to delete this message. You can find it later.")

        await ctx.send()


def setup(client):
    client.add_cog(NitroBooster(client))
