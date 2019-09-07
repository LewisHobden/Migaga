from discord.ext import commands

import discord


class People(commands.Cog):
    """ Commands relating to getting details on people. """

    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def info(self, ctx, member: discord.Member = None):
        """ Get information on yourself or another user! """
        member = member if member else ctx.author

        embed = discord.Embed(description="Info for " + member.display_name, image=member.avatar_url, colour=7576022)

        embed.set_author(name=str(member), icon_url=member.avatar_url)

        embed.add_field(name="Created:", value=member.created_at.strftime("%d of %b %Y at\n%H:%M:%S"))
        embed.add_field(name="Joined Server:", value=member.joined_at.strftime("%d of %b %Y at\n%H:%M:%S"))
        embed.add_field(name="ID:", value=member.id)

        # embed.add_field(name="Infractions:", value=await self.getTotalInfractions(member.id))
        # embed.add_field(name="Money:", value=await self.getTotalInfractions(member.id))
        embed.add_field(name="Discriminator:", value="#" + member.discriminator)

        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def warnings(self, ctx):
        """ See what warnings you've been given! """
        user_warnings = await self.getWarningsForUser(ctx.message.author.id, ctx.message.guild.id)
        member = ctx.message.author

        embed = discord.Embed(description="Warnings for " + member.display_name, colour=7576022)

        avatar = member.avatar_url if member.avatar else member.default_avatar_url
        embed.set_author(name=str(member), icon_url=avatar)

        reasons = ""
        types = ""
        times = ""
        for warning in user_warnings:
            reasons += warning["reason"] + "\n"
            types += await self.convertWarningTypeToText(warning["type"]) + "\n"
            times += warning["time_warned"].strftime("%d of %b (%Y) %H:%M:%S") + "\n"

        embed.add_field(name="Reason: ", value=reasons)
        embed.add_field(name="Type: ", value=types)
        embed.add_field(name="Time: ", value=times)

        try:
            await self.client.send_message(ctx.message.channel, embed=embed)
        except:
            await self.client.send(
                "There was an error, it's likely they have too many warnings to fit on one screen. I'm working on formatting this better - however I recommend you ban somebody with this many warnings :l")

    @commands.command(pass_context=True)
    async def avatar(self, ctx, member: discord.Member = None):
        """ Shows a bigger version of somebody's Avatar! """
        member = member if member else ctx.message.author

        await ctx.send(member.avatar_url)


def setup(client):
    client.add_cog(People(client))
