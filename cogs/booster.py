import datetime
from datetime import datetime

import discord
from discord import TextChannel, Member, Role, Colour
from discord.ext import commands
from discord.ext.commands import ColourConverter
from discord_slash import cog_ext, SlashCommandOptionType, SlashContext
from peewee import DoesNotExist

from model.model import BoosterMessage, BoosterRole


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


class BoosterRoleEmbed(discord.Embed):
    def __init__(self, role: Role, prefix: str, include_instructions=True, **kwargs):
        kwargs['colour'] = role.colour
        kwargs['title'] = "Booster Role"
        kwargs['timestamp'] = datetime.utcnow()

        super().__init__(**kwargs)

        self.add_field(name="Colour", value=role.colour.to_rgb())
        self.add_field(name="Role Name", value=role.name)

        if include_instructions:
            self.set_footer(text="Tip: use the command {}help br for details on how to update your role".format(prefix))


class BoosterRoleController:
    def __init__(self, role: Role):
        self.role = role

    async def set_role_attribute(self, ctx, attribute: str, value: str):
        if attribute.lower() in ["name", "title"]:  # Update the title
            await self.role.edit(name=value)

        if attribute.lower() in ["color", "colour"]:  # Update the colour
            converter = ColourConverter()
            colour = await converter.convert(ctx, value)

            await self.role.edit(colour=colour, reason="Requested using the Booster Role command.")


class BoosterMessageController:
    def __init__(self, message: str):
        self.message = message

    def format_message(self, member: discord.Member) -> str:
        parsable_message = self.message.replace("<@>", "{0}").replace("<>", "{1}").replace("<s>", "{2}")

        return parsable_message.format(member.mention, member.display_name, member.guild.name)

    async def send_boost_message(self, destination: TextChannel, booster: discord.Member):
        await destination.send(self.format_message(booster))


class BoosterRoleCog(commands.Cog, name="Booster Roles"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="boosterrole", aliases=["br", "myrole"])
    async def _booster_role(self, ctx, instruction: str = None, field: str = None, *, value: str = None):
        """ A command that allows you to edit your own booster role! You must Nitro boost this server for it to work.

            Edit your role using "set" and then "name" or "colour".

            i.e. `!boosterrole set name [name]` would update your role name.
            or `!boosterrole set colour [colour]` would update your role colour.
        """
        # if not ctx.author.premium_since:
        #     return await ctx.reply("You must boost this server in order to use this command!")
        msg = await ctx.reply("Getting that ready for you!")
        stored_role = BoosterRole.get_for_member(ctx.author)
        role = None

        if not stored_role:
            await msg.edit(content="You don't have a booster role just yet, I'll set you up one now...")

            role = await ctx.guild.create_role(name="Test Booster Role Name")
            stored_role = BoosterRole.add_for_member(ctx.author, role)

            await ctx.author.add_roles(role)

        if role is None:
            role = ctx.guild.get_role(stored_role.role_id)

            if role is None:
                stored_role.delete_instance()

                return await msg.edit(content="I can't find your role! Perhaps an admin has deleted it. I'll fix it, "
                                              "please run the command again!")

        if instruction in ["set", "edit"] and field is not None and value is not None:
            controller = BoosterRoleController(role)
            await controller.set_role_attribute(ctx, field, value)

            role = controller.role

        return await msg.edit(content="", embed=BoosterRoleEmbed(role, ctx.prefix))


class BoosterNotificationCog(commands.Cog):
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
            await ctx.send(
                embed=BoosterMessageEmbed(message=stored_message, member=ctx.author, title="Booster Notification"))

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
    client.add_cog(BoosterRoleCog(client))
    client.add_cog(BoosterNotificationCog(client))
