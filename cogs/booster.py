import datetime
import discord
from datetime import datetime
from discord import TextChannel, Member, message
from discord.ext import commands
from discord_slash import cog_ext, SlashCommandOptionType, SlashContext
from peewee import DoesNotExist

from model.model import BoosterMessage


class BoosterMessageEmbed(discord.Embed):
    def __init__(self, message: BoosterMessage, member: Member, **kwargs):
        controller = BoosterMessageController(message.message)

        kwargs['colour'] = discord.Colour.purple()
        kwargs['description'] = controller.format_message(member)
        kwargs['timestamp'] = datetime.utcnow()

        super().__init__(**kwargs)

        self.add_field(name="Channel", value="<#{}>".format(message.channel_id))
        self.add_field(name="Reference", value=message.reference)

        self.set_footer(text="The \"reference\" is used to delete this message.")


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

    @cog_ext.cog_subcommand(base="booster", subcommand_group="notification", name="add",
                            description="Sets up a new message for when somebody boosts the guild.",
                            guild_ids=[197972184466063381],
                            options=[{"name": "channel", "description": "The channel to post the message in.",
                                      "type": SlashCommandOptionType.CHANNEL, "required": True},
                                     {"name": "message",
                                      "description": "The message to post. You can use placeholders!",
                                      "type": SlashCommandOptionType.STRING, "required": True}])
    @commands.has_permissions(manage_guild=True)
    async def _add_message(self, ctx: SlashContext, channel: TextChannel, message: str):
        if not isinstance(channel, discord.TextChannel):
            return await ctx.send("That channel type isn't supported!")

        db_message = BoosterMessage.add_for_guild(ctx.guild_id, channel, message)

        await ctx.send(embed=BoosterMessageEmbed(message=db_message, member=ctx.author, title="New Message Added!"))

    @cog_ext.cog_subcommand(base="booster", subcommand_group="notification", name="delete",
                            description="Deletes a booster notification from the guild.",
                            guild_ids=[197972184466063381],
                            options=[{"name": "reference", "description": "The reference of the message to delete.",
                                      "type": SlashCommandOptionType.STRING, "required": True}])
    @commands.has_permissions(manage_guild=True)
    async def _delete_message(self, ctx: SlashContext, reference: str):
        try:
            stored_message = BoosterMessage.get_by_id(reference)
        except DoesNotExist:
            return await ctx.send("A message could not be found for that ID. Try listing the messages?")

        stored_message.delete_instance()

        await ctx.send("Message was deleted successfully!")

    @cog_ext.cog_subcommand(base="booster", subcommand_group="notification", name="list",
                            description="Lists all booster notifications in your guild.",
                            guild_ids=[197972184466063381],
                            options=[{"name": "channel", "description": "The channel specifically to search.",
                                      "type": SlashCommandOptionType.CHANNEL, "required": False}])
    @commands.has_permissions(manage_guild=True)
    async def _list_messages(self, ctx: SlashContext, channel: TextChannel = None):
        if channel is not None and not isinstance(channel, discord.TextChannel):
            return await ctx.send("That channel type isn't supported!")

        stored_messages = BoosterMessage.get_for_guild(ctx.guild, channel)

        for stored_message in stored_messages:
            await ctx.send(embed=BoosterMessageEmbed(message=stored_message, member=ctx.author, title="Booster Notification"))

    async def _on_member_updated(self, member_before: Member, member_after: Member):
        if not (member_before.premium_since is None and member_after.premium_since is not None):
            return

        boost_messages = BoosterMessage.get_for_guild(member_after.guild)

        if len(boost_messages) < 1:
            return

        for boost_message in boost_messages:
            try:
                destination = self.client.get_channel(boost_message.channel_id)
            except discord.NotFound:
                continue  # Should we delete the message from the database?

            controller = BoosterMessageController(boost_message.message)
            await controller.send_boost_message(destination, member_after)


def setup(client):
    client.add_cog(NitroBooster(client))
