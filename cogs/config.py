from discord.ext import commands

import discord
from discord.ext.commands import TextChannelConverter, PartialEmojiConverter, EmojiConverter

from model.model import GuildConfig


class Config(commands.Cog):
    """ Settings and configuration for tweaking the bot in your server. """

    def __init__(self, client: commands.Bot):
        self.client = client

    async def _alter_config(self, ctx: commands.Context, config: GuildConfig, action, value=None):
        # Route the user based on their input.
        channel_converter = TextChannelConverter()
        emoji_converter = EmojiConverter()

        if action == "logs":
            if value is None:
                channel_id = None
            else:
                channel = await channel_converter.convert(ctx=ctx, argument=value)
                channel_id = channel.id

            config.server_logs_channel_id = channel_id

        elif action == "points":
            if value is None:
                name = None
            else:
                name = value.strip()

            config.points_name = name

        elif action == "points-emoji":
            if value is None:
                emoji = None
            else:
                emoji = await emoji_converter.convert(ctx=ctx, argument=value)

            config.points_emoji = emoji

        elif action == "starboard-emoji":
            if value is None:
                emoji_id = None
            else:
                emoji = await emoji_converter.convert(ctx=ctx, argument=value)
                emoji_id = emoji.id

            config.starboard_emoji_id = emoji_id

        # If someone tries to "Remove" a config option, re-run the command but with an empty val.
        elif action == "remove":
            return await self._alter_config(ctx=ctx, config=config, action=value, value=None)

        else:
            return await ctx.send("I'm not sure what config option you want me to update! Your options are: "
                                  "logs, points, points-emoji, starboard-emoji, remove")

        config.save()
        await ctx.send("Your server logs have been updated!")
        await self._display_config(ctx, config)

    async def _display_config(self, ctx: commands.Context, guild_config: GuildConfig):
        embed = discord.Embed(color=discord.Color.blue(), title="Your Config",
                              description="These are all the config settings for your server.")

        logs_channel = "Not Enabled"

        if guild_config.server_logs_channel_id is not None:
            logs_channel = self.client.get_channel(guild_config.server_logs_channel_id).mention

        starboard_emoji = "⭐"

        if guild_config.starboard_emoji_id is not None:
            starboard_emoji = self.client.get_emoji(guild_config.starboard_emoji_id)

        points_emoji = "*Not Setup*"
        if guild_config.points_emoji is not None:
            points_emoji = guild_config.points_emoji

        embed.add_field(name="Server Logs", value=logs_channel)
        embed.add_field(name="Points", value=guild_config.points_name if not None else "*Not Setup*")
        embed.add_field(name="Points Emoji", value=points_emoji)
        embed.add_field(name="Starboard Emoji", value=starboard_emoji)

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
