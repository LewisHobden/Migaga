import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

from model.embeds import ConfigEmbed
from model.model import GuildConfig


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(base="config", name="points-emoji", guild_ids=[197972184466063381])
    @commands.has_permissions(manage_guild=True)
    async def _points_emoji(self, ctx: SlashContext, emoji: discord.Emoji):
        guild_config = await GuildConfig.get_for_guild(ctx.guild.id)
        guild_config.points_emoji = emoji
        guild_config.save()

        embed = ConfigEmbed(guild_config=guild_config)
        await ctx.send(content="Config has been updated.", embeds=[embed])


def setup(bot):
    bot.add_cog(Slash(bot))
