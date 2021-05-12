import discord
from discord.ext import commands
from discord.ext.commands import RoleConverter, RoleNotFound
from discord_slash import cog_ext, SlashContext, SlashCommandOptionType

from cogs.utilities.formatting import format_points
from model.embeds import LeaderboardEmbed
from model.model import *


def _populate_embed_from_guild(embed: LeaderboardEmbed, guild: Guild):
    index = 1
    for transaction in PointTransaction.get_leaderboard_for_guild(guild):
        member = guild.get_member(transaction.recipient_user_id)

        embed.add_entry(index, member.display_name, transaction.total_points)
        index += 1


async def _populate_embed_from_leaderboard(embed: LeaderboardEmbed, leaderboard_name: str, guild: Guild):
    leaderboard = await PointLeaderboard.get_for_guild(guild, leaderboard_name)

    if leaderboard is None:
        return

    # Iterate the teams, query the DB for their total points.
    index = 1
    indexed_teams = {}
    for team in leaderboard.teams:
        team = guild.get_role(team.discord_role_id)
        members = map(lambda x: x.id, team.members)

        total_points = PointTransaction.get_total_for_guild_members(guild, list(members))
        indexed_teams[team.name] = float(total_points)

    for team_name in sorted(indexed_teams, key=indexed_teams.get, reverse=True):
        embed.add_entry(index, team_name, indexed_teams[team_name])

        index += 1


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
                                  format_points(amount),
                                  config,
                                  "" if config.points_emoji is None else " " + config.points_emoji),
                              color=discord.Color.green())

        embed.add_field(name="New total for {.display_name}".format(ctx.author),
                        value=format_points(await PointTransaction.get_total_for_member(ctx.author)))

        embed.add_field(name="New total for {.display_name}".format(member),
                        value=format_points(await PointTransaction.get_total_for_member(member)))

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
        position = await PointTransaction.get_position_in_guild_leaderboard(ctx.guild.id, member.id)

        if user_total is None:
            return await ctx.send("No points earned yet!")

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
    async def leaderboard(self, ctx, *, leaderboard_name: str = None):
        """ Shows the leaderboard for the server.

         If your server has custom leaderboards, you can provide the leaderboard's name to get that. """
        config = await GuildConfig.get_for_guild(ctx.guild.id)

        if config.points_name is None:
            return await ctx.send("A server admin needs to set up points using the points config command!")

        embed = LeaderboardEmbed(colour=discord.Colour.gold(), config=config, guild=ctx.guild)

        if leaderboard_name:
            await _populate_embed_from_leaderboard(embed, leaderboard_name, ctx.guild)
        else:
            _populate_embed_from_guild(embed, ctx.guild)

        await ctx.send(embed=embed.populate())

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
        elif action not in {"give", "add"}:
            return await ctx.send("You can either \"give\" or \"take\" points. See the help command for help.")

        if amount < 0:
            emoji = "\U0001f4c9"
            action = "Lost"
        else:
            emoji = "\U0001f4c8"
            action = "Got"

        await PointTransaction.grant_member(amount, member, ctx.author)
        user_total = await PointTransaction.get_total_for_member(member)

        embed = discord.Embed(title="{0} Points {1} {0}".format(emoji, action),
                              description="{.mention} just {} some {.points_name}{}".format(member, action.lower(),
                                                                                            config,
                                                                                            "" if config.points_emoji is None else " " + config.points_emoji),
                              color=discord.Color.green())

        embed.add_field(name="Total {}".format(action), value=str(abs(amount)))
        embed.add_field(name="New Total", value=format_points(user_total))

        # If the user exists in 1 or more teams, add a field to the embed about it.
        teams = filter(lambda x: PointLeaderboardTeam.exists_for_role(x), member.roles)
        team_message = ", ".join(map(lambda x: x.name, teams))

        if len(team_message):
            embed.add_field(name="Helped out their teams!", value=team_message, inline=False)

        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(base="points", name="setup-leaderboard",
                            description="Sets up a new leaderboard, provided a list of roles that are in it.",
                            options=[
                                {"name": "leaderboard_name", "description": "The name of the leaderboard.", "type": SlashCommandOptionType.STRING,
                                 "required": True},
                                {"name": "roles",
                                 "description": "Comma-separated list of roles that are in the leaderboard.", "type": SlashCommandOptionType.STRING,
                                 "required": True},
                            ])
    @commands.has_permissions(manage_guild=True)
    async def _setup_team(self, ctx: SlashContext, leaderboard_name: str, roles: str):
        errors = []
        role_converter = RoleConverter()
        role_objects = []

        for role in roles.split(","):
            try:
                role_objects.append(await role_converter.convert(ctx, role.strip()))
            except RoleNotFound:
                errors.append("Role could not be found: {}".format(role))

        if errors:
            return await ctx.send("\n".join(errors))

        try:
            leaderboard = await PointLeaderboard.add_for_guild(ctx.guild, leaderboard_name, role_objects)
            await ctx.send("Boom! You've got a new leaderboard setup for those roles.".format(leaderboard.id))
        except IntegrityError as e:
            await ctx.send(str(e))


def setup(client: commands.Bot):
    client.add_cog(Points(client))
