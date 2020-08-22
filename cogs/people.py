from discord.ext import commands

import discord


class People(commands.Cog):
    """ Commands relating to getting details on people. """

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def info(self, ctx, member: discord.Member = None):
        """ Get information on yourself or another user! """
        member = member if member else ctx.author

        embed = discord.Embed(description="Info for " + member.display_name, image=member.avatar_url, colour=7576022)

        embed.set_author(name=str(member), icon_url=member.avatar_url)

        embed.add_field(name="Created:", value=member.created_at.strftime("%d of %b %Y at\n%H:%M:%S"))
        embed.add_field(name="Joined Server:", value=member.joined_at.strftime("%d of %b %Y at\n%H:%M:%S"))
        embed.add_field(name="ID:", value=member.id)

        embed.add_field(name="Discriminator:", value="#" + member.discriminator)

        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        """ Shows a bigger version of somebody's Avatar! """
        member = member if member else ctx.message.author

        await ctx.send(member.avatar_url)


def setup(client):
    client.add_cog(People(client))
