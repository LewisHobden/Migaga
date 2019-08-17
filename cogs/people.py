from discord.ext import commands
from cogs.utilities import credential_checks
from cogs.games.currency import Money
from cogs.customcommands import connectToDatabase
from cogs.utilities.tools import Tools

import discord
import datetime
import asyncio
import logging
import pymysql
import random
import time

class People(commands.Cog):
    """ Commands relating to getting details on people. """
    def __init__(self, client):
        self.client = client

    async def getTotalInfractions(self, user_id):
        connection = connectToDatabase()
        with connection.cursor() as csr:
            sql = "SELECT COUNT(*) AS `total` FROM `discord_warnings` WHERE `user_id`=%s"
            csr.execute(sql, user_id)

            return csr.fetchone()["total"]

    async def getTotalSentMessages(self, user_id):
        connection = connectToDatabase()
        with connection.cursor() as csr:
            sql = "SELECT `messages_sent` FROM `discord_persons` WHERE `user_id`=%s"
            csr.execute(sql, user_id)

            return csr.fetchone()["messages_sent"]

    async def getWarningsForUser(self, user_id, server_id):
        connection = connectToDatabase()
        warnings = []
        server_id = "84142598456901632"
        with connection.cursor() as csr:
            sql = "SELECT `reason`, `type`, `time_warned` FROM `discord_warnings` WHERE `user_id`=%s AND `server_id`=%s"
            csr.execute(sql, [user_id, server_id])

            for result in csr:
                warnings.append(result)

        return warnings

    async def convertWarningTypeToText(self, warning_type):
        if warning_type == 0:
            return "Warning"
        elif warning_type == 1:
            return "Mute"
        elif warning_type == 2:
            return "Kick"
        else:
            return "unknown type"

    async def renderInfoAsEmbed(self, member):
        embed = discord.Embed(description="Info for "+member.display_name, image=member.avatar_url, colour=7576022)

        avatar = member.avatar_url if member.avatar else member.default_avatar_url
        embed.set_author(name=str(member), icon_url=avatar)

        embed.add_field(name="Created:", value=member.created_at.strftime("%d of %b %Y at\n%H:%M:%S"))
        embed.add_field(name="Joined Server:", value=member.joined_at.strftime("%d of %b %Y at\n%H:%M:%S"))
        embed.add_field(name="ID:", value=member.id)

        embed.add_field(name="Infractions:", value=await self.getTotalInfractions(member.id))
        embed.add_field(name="Discriminator:", value="#"+member.discriminator)
        embed.add_field(name="Messages Sent:", value=await self.getTotalSentMessages(member.id))

        return embed

    @commands.command(pass_context=True)
    async def userinfo(self, ctx, member : discord.Member = None):
        """ Get information on another user! """
        embed = await self.renderInfoAsEmbed(member if member else ctx.message.author)

        await self.client.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def warnings(self, ctx):
        """ See what warnings you've been given! """
        user_warnings = await self.getWarningsForUser(ctx.message.author.id, ctx.message.server.id)
        member = ctx.message.author

        embed = discord.Embed(description="Warnings for "+member.display_name, colour=7576022)

        avatar = member.avatar_url if member.avatar else member.default_avatar_url
        embed.set_author(name=str(member), icon_url=avatar)

        reasons = ""
        types   = ""
        times   = ""
        for warning in user_warnings:
            reasons += warning["reason"]+"\n"
            types   += await self.convertWarningTypeToText(warning["type"])+"\n"
            times   += warning["time_warned"].strftime("%d of %b (%Y) %H:%M:%S")+"\n"

        embed.add_field(name="Reason: ", value=reasons)
        embed.add_field(name="Type: ", value=types)
        embed.add_field(name="Time: ", value=times)

        try:
            await self.client.send_message(ctx.message.channel, embed=embed)
        except:
            await self.client.say("There was an error, it's likely they have too many warnings to fit on one screen. I'm working on formatting this better - however I recommend you ban somebody with this many warnings :l")

    async def getUserProfileInformation(self, user_id):
        connection = connectToDatabase()
        with connection.cursor() as csr:
            sql = "SELECT * FROM `discord_profiles` WHERE `user_id`=%s"
            csr.execute(sql, user_id)

            for row in csr:
                return row

    async def makeProfileEmbedFromUser(self, member):
        profile = await self.getUserProfileInformation(member.id)
        if None == profile:
            return None

        embed = discord.Embed(colour=await Tools.ifNoneReplaceWith(Tools, profile["colour"], discord.Colour.teal()), description=await Tools.ifNoneReplaceWith(Tools, profile["message"], ""), title=await Tools.ifNoneReplaceWith(Tools, profile["tag"], member.display_name))
        embed.add_field(name="NNID:", value=await Tools.ifNoneReplaceWith(Tools, profile["nnid"], "Not set"))
        embed.add_field(name="Region:", value=await Tools.ifNoneReplaceWith(Tools, profile["region"], "Not Set"))
        embed.add_field(name="Main:", value=await Tools.ifNoneReplaceWith(Tools, profile["main"], "Not Set"))
        embed.add_field(name="Twitter:", value=await Tools.ifNoneReplaceWith(Tools, profile["twitter"], "Not Set"))

        avatar = member.avatar_url if member.avatar else member.default_avatar_url
        embed.set_author(name=str(member), icon_url=avatar)

        return embed

    @commands.command(pass_context=True)
    async def profile(self, ctx, member : discord.Member = None):
        """ View your own profile! """
        embed = await self.makeProfileEmbedFromUser(member if member else ctx.message.author)

        if None == embed:
            await self.client.say("This user does not have a profile!")
            return

        await self.client.send_message(ctx.message.channel, embed=embed)


    @commands.command(pass_context=True)
    async def set(self, ctx, field, *, response):
        """ Set a field of your profile!

        Possible fields:
        - Colour
        - Message
        - Tag
        - NNID
        - Region
        - Main
        - Twitter"""
        connection = connectToDatabase()

        if field == "color" or field == "colour":
            field = "colour"
            if response[:1] == "#":
                response = int(response[1:], 16)

        with connection.cursor() as csr:
            sql = "INSERT INTO `discord_profiles`(`user_id`, `"+connection.escape(field)[1:-1]+"`) VALUES (%(user_id)s, %(response)s) ON DUPLICATE KEY UPDATE `discord_profiles`.`"+connection.escape(field)[1:-1]+"`=%(response)s"
            try:
                csr.execute(sql, {"response" : response, "user_id" : ctx.message.author.id})
                await self.client.say("Successfully set your `"+field+"` to `"+str(response)+"`!")
            except:
                await self.client.say("Setting your `"+field+"` failed! Perhaps it doesn't exist yet?")
                return

    @commands.command()
    async def avatar(self, member : discord.Member):
        """ Shows a bigger version of somebody's Avatar! """
        avatar = member.avatar_url if member.avatar else member.default_avatar_url
        await self.client.say(avatar)


def setup(client):
    client.add_cog(People(client))
