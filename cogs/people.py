from discord.ext import commands
from peewee import *
from cogs.utilities.tools import Tools
from model.profile import Profile
from model.profile_field import ProfileField

import discord


async def _profile_embed(member: discord.Member):
    try:
        profile = Profile.get_by_id(member.id)
    except DoesNotExist:
        return None

    embed = discord.Embed(colour=discord.Colour(profile.colour), description=profile.bio, title=profile.tag)

    for field in profile.fields:
        embed.add_field(name=field.key, value=field.value)

    embed.set_author(name=str(member), icon_url=member.avatar_url)

    return embed


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
    async def profile(self, ctx, member: discord.Member = None):
        """ View your own profile! """
        embed = await _profile_embed(member if member else ctx.message.author)

        if embed is None:
            if member is None:
                message = "You do not have a profile yet. Set it up with `!myprofile`"
            else:
                message = "This user does not have a profile!"

            await ctx.send(message)
            return

        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def myprofile(self, ctx, colour: discord.Colour, tag: str, *, bio: str):
        """ Set up or edit your main profile. Use the help command for required parts. """
        Profile.insert(discord_user_id=ctx.author.id, colour=colour.value, tag=tag, bio=bio)\
            .on_conflict_replace(True)\
            .execute()

        await ctx.send("Profile set up! Thank you! Here it is!", embed=await _profile_embed(ctx.author))

    @commands.command(pass_context=True)
    async def set(self, ctx, field, *, value):
        """ Set a custom field of your profile!"""
        try:
            Profile.get_by_id(ctx.author.id)
        except DoesNotExist:
            await ctx.send("You don't have a profile. Set one up using `!myprofile`")

        ProfileField.insert(discord_user_id=ctx.author.id, key=field, value=value).on_conflict_replace(True).execute()

        await ctx.send("Successfully set your `" + field + "` to `" + str(value) + "`!")

    @commands.command(pass_context=True)
    async def avatar(self, ctx, member: discord.Member = None):
        """ Shows a bigger version of somebody's Avatar! """
        member = member if member else ctx.message.author

        await ctx.send(member.avatar_url)


def setup(client):
    client.add_cog(People(client))
