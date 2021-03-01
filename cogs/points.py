import discord
from discord.ext import commands

from cogs.utilities.formatting import format_points
from model.model import *


class Points(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def gift(self, ctx, member: discord.Member, amount: float):
        """ Gifts points to another member of your Guild, you need to have the right amount! """
        config = await GuildConfig.get_for_guild(member.guild.id)
        user_total = await PointTransaction.get_total_for_member(ctx.author)

        if amount <= 0:
            await ctx.send("Nice try, you can't give negative points!")
            return

        if amount > user_total:
            await ctx.send("You can't give that many points!")
            return

        await PointTransaction.grant_member(amount, member, ctx.author)
        await PointTransaction.grant_member(-amount, ctx.author, ctx.author)

        emoji = "\U0001F381"
        embed = discord.Embed(title="{0} Points Gifted! {0}".format(emoji),
                              description="{.mention} just gifted {.mention} {} {.points_name}{}".format(
                                  ctx.author,
                                  member,
                                  amount,
                                  config,
                                  "" if config.points_emoji is None else " " + config.points_emoji),
                              color=discord.Color.green())

        await ctx.send(embed=embed)

    @commands.command()
    async def inventory(self, ctx, *, member: discord.Member = None):
        """ Gets the number of points you have in yours or someone else's inventory. """
        if member is None:
            member = ctx.author

        config = await GuildConfig.get_for_guild(member.guild.id)

        if config.points_name is None:
            return

        user_total = await PointTransaction.get_total_for_member(member)
        position = await PointTransaction.get_position_in_guild_leaderboard(ctx.guild.id, ctx.author.id)

        embed = discord.Embed(title="", color=member.colour)
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)

        if config.points_emoji:
            emoji_id = config.points_emoji.split(":")[2][:-1]
            points_emoji = discord.utils.get(ctx.guild.emojis, id=int(emoji_id))

            if points_emoji:
                embed.set_thumbnail(url=points_emoji.url)

        embed.add_field(name="Total", value="{} {.points_name}".format(format_points(user_total), config), inline=False)
        embed.add_field(name="Leaderboard Position", value="#{} in {.name}".format(position[0], ctx.guild),
                        inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        """ Shows the leaderboard for the server.

         If you mention a person then you can get your placement on the leaderboard. """
        config = await GuildConfig.get_for_guild(ctx.guild.id)

        if config.points_name is None:
            return
        transactions = (PointTransaction
                        .select(PointTransaction.recipient_user_id,
                                fn.SUM(PointTransaction.amount).alias('total_points'))
                        .where(PointTransaction.guild_id == ctx.guild.id)
                        .group_by(PointTransaction.recipient_user_id)
                        .order_by(SQL('total_points DESC'))
                        .limit(10))

        body = "Showing the Top 10..\n"

        index = 1
        for transaction in transactions:
            member = ctx.guild.get_member(transaction.recipient_user_id)
            points = config.points_name[0].upper()
            points += config.points_name[1:]

            body += ("{}. **{}** - {}\n".format(index, member.display_name, format_points(transaction.total_points)))
            index += 1

        e = discord.Embed(colour=discord.Colour.gold(),
                          title="{} Leaderboard for {}".format(points, ctx.guild.name),
                          description=body)

        await ctx.send(embed=e)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def points(self, ctx, action: str, member: discord.Member, amount: float):
        """ Give or takes away points from a user based on the action and how much you define.
        Your action is "give" or "take".. example, !points remove @Migaga 10

        You will need "Manage Roles" permissions to do this. """
        # Update the DB.
        config = await GuildConfig.get_for_guild(ctx.guild.id)

        if config.points_name is None:
            await ctx.send("You have not set up points in this server yet. Use `!config` to get started!")
            return

        if action in {"take", "remove"}:
            amount = amount * -1
            emoji = "\U0001f4c9"
            action = "Lost"
        elif action in {"give", "add"}:
            emoji = "\U0001f4c8"
            action = "Got"
        else:
            return await ctx.send("You can either \"give\" or \"take\" points. See the help command for help.")

        await PointTransaction.grant_member(amount, member, ctx.author)
        user_total = await PointTransaction.get_total_for_member(member)

        embed = discord.Embed(title="{0} Points {1} {0}".format(emoji, action),
                              description="{.mention} just {} some {.points_name}{}".format(member, action.lower(),
                                                                                            config,
                                                                                            "" if config.points_emoji is None else " " + config.points_emoji),
                              color=discord.Color.green())

        embed.add_field(name="Total {}".format(action), value=str(abs(amount)))
        embed.add_field(name="New Total", value=format_points(user_total))

        await ctx.send(embed=embed)


def setup(client: commands.Bot):
    client.add_cog(Points(client))
