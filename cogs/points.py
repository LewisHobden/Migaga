import typing

import discord
from discord.ext import commands

from model.model import *


def _format_total(total: typing.Optional[float]) -> str:
    if total is None:
        return "0"

    return '{0:.3f}'.format(total)


class Points(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def inventory(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        config = await GuildConfig.get_for_guild(member.guild.id)

        if config.points_name is None:
            return

        user_total = await PointTransaction.get_total_for_member(member)

        emoji = "" if config.points_emoji is None else " " + config.points_emoji
        embed = discord.Embed(title="In {.name}".format(member.guild), color=discord.Color.green())
        embed.description = "{.display_name} has {} {.points_name}{}".format(member, _format_total(user_total), config,
                                                                             emoji)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def pointsetup(self, ctx, name: str, emoji: discord.Emoji = None):
        """ Sets up points in your server. Points need a name and optionally they need an emoji.

        You will need "Manage Server" permissions to do this. """
        config = await GuildConfig.get_for_guild(ctx.guild.id)

        config.points_name = name.strip()
        config.points_emoji = emoji

        config.save()

        embed = discord.Embed(title="Points Configured", description="Your points are set up!",
                              color=discord.Color.green())

        embed.add_field(name="Name", value=name)

        if emoji is not None:
            embed.add_field(name="Emoji", value=str(emoji))

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def points(self, ctx, action: str, member: discord.Member, amount: float):
        """ Gives a user some points, however much you define.
        Your action is "give" or "remove".. example, !points remove @Migaga 10

        You will need "Manage Roles" permissions to do this. """
        # Update the DB.
        config = await GuildConfig.get_for_guild(ctx.guild.id)

        if config.points_name is None:
            await ctx.send("You have not set up points in this server yet. Use `!pointsetup` to get started!")
            return

        if "remove" == action:
            amount = amount * -1
            emoji = "\U0001f4c9"
            action = "Lost"
        elif "give" == action:
            emoji = "\U0001f4c8"
            action = "Got"
        else:
            return await ctx.send("You can either \"give\" or \"remove\" points. See the help command for help.")

        await PointTransaction.grant_member(amount, member, ctx.author)
        user_total = await PointTransaction.get_total_for_member(member)

        embed = discord.Embed(title="{0} Points {1} {0}".format(emoji, action),
                              description="{.mention} just {} some {.points_name}{}".format(member, action.lower(),
                                                                                            config,
                                                                                            "" if config.points_emoji is None else " " + config.points_emoji),
                              color=discord.Color.green())

        embed.add_field(name="Total {}".format(action), value=str(abs(amount)))
        embed.add_field(name="New Total", value=_format_total(user_total))

        await ctx.send(embed=embed)


def setup(client: commands.Bot):
    client.add_cog(Points(client))
