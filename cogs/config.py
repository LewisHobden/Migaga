from discord.ext import commands
from discord.ext.commands import PartialEmojiConversionFailure
from discord_slash import SlashContext, cog_ext

from converters.converters import PartialEmojiWithUnicodeConverter
from model.embeds import ConfigEmbed
from model.model import GuildConfig


class Config(commands.Cog):
    """ Settings and configuration for tweaking the bot in your server. """

    def __init__(self, client: commands.Bot):
        self.client = client

    @cog_ext.cog_subcommand(base="config", name="points",
                            description="Configures the name of your points in this server.",
                            options=[{"name": "points", "description": "The custom name of your points, e.g. rupees.", "type": 3, "required": True}])
    @commands.has_permissions(manage_guild=True)
    async def _points(self, ctx: SlashContext, points: str):
        guild_config = await GuildConfig.get_for_guild(ctx.guild.id)
        guild_config.points_name = points
        guild_config.save()

        embed = ConfigEmbed(guild_config=guild_config)
        await ctx.send(content="Config has been updated.", embeds=[embed])

    @cog_ext.cog_subcommand(base="config", name="points-emoji",
                            description="Configures the custom emoji for points in this server.",
                            options=[{"name": "emoji", "description": "The emoji to be displayed next to your points when they are displayed.", "type": 3, "required": True}])
    @commands.has_permissions(manage_guild=True)
    async def _points_emoji(self, ctx: SlashContext, emoji: str):
        emoji_converter = PartialEmojiWithUnicodeConverter()

        try:
            emoji = await emoji_converter.convert(ctx, emoji)
        except PartialEmojiConversionFailure:
            return await ctx.send("Unknown emoji: {}".format(emoji))

        if emoji not in ctx.guild.emojis and not isinstance(emoji, str):
            await ctx.send("Warning, the emoji you have picked doesn't exist in this server. It could be deleted "
                           "without your knowledge!")

        guild_config = await GuildConfig.get_for_guild(ctx.guild.id)
        guild_config.points_emoji = str(emoji)
        guild_config.save()

        embed = ConfigEmbed(guild_config=guild_config)
        await ctx.send(content="Config has been updated.", embeds=[embed])


def setup(client):
    client.add_cog(Config(client))
