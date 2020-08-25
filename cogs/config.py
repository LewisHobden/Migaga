from discord.ext import commands

import discord
from discord.ext.commands import TextChannelConverter

from model.model import GuildConfig


class Config(commands.Cog):
    """ Settings and configuration for tweaking the bot in your server. """

    def __init__(self, client: commands.Bot):
        self.client = client

    async def _alter_config(self, ctx: commands.Context, config: GuildConfig, action, value=None):
        # Route the user based on their input.
        channel_converter = TextChannelConverter()

        if action == "logs":
            if value is None:
                channel_id = None
            else:
                channel = await channel_converter.convert(ctx=ctx, argument=value)
                channel_id = channel.id

            config.server_logs_channel_id = channel_id
            config.save()
            await ctx.send("Your server logs have been updated!")
            await self._display_config(ctx, config)

            return

        # If someone tries to "Remove" a config option, re-run the command but with an empty val.
        if action == "remove":
            return self._alter_config(ctx=ctx, config=config, action=value, value=None)

        return ctx.send("I'm not sure what config option you want me to update! Your options are: "
                        "logs, remove")

    async def _display_config(self, ctx: commands.Context, guild_config: GuildConfig):
        embed = discord.Embed(color=discord.Color.blue(), title="Your Config",
                              description="These are all the config settings for your server.")

        logs_channel = "Not Enabled"

        if guild_config.server_logs_channel_id is not None:
            logs_channel = self.client.get_channel(guild_config.server_logs_channel_id).mention

        embed.add_field(name="Server Logs", value=logs_channel)
        embed.add_field(name="Points", value=guild_config.points_name if not None else "Not Enabled")

        return await ctx.send(embed=embed)

    @commands.command()
    async def config(self, ctx, action=None, *, value=None):
        """
        Allows you to tweak configuration settings or view what your server currently does.

        You need "Manage Guild" permissions in order to use this command.
        My attempt at a different style command. It routes the user based on the number of arguments they provide.
        """
        guild_config = await GuildConfig.get_for_guild(ctx.guild.id)

        if action is None:
            return await self._display_config(ctx, guild_config)

        return await self._alter_config(ctx, guild_config, action, value)


def setup(client):
    client.add_cog(Config(client))
