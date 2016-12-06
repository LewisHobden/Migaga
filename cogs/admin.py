from discord.ext import commands
from cogs.utilities import credential_checks

import discord
import datetime
import logging

log = logging.getLogger(__name__)

class Admin:
    """Moderation related commands."""
    def __init__(self, client):
        self.client = client

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member):
        """Bans a member from the server.
        In order to do this, the bot and you must have Ban Member permissions.
        """
        try:
            await self.client.ban(member)
        except discord.Forbidden:
            await self.client.say("The bot does not have permissions to kick members.")
        except discord.HTTPException:
            await self.client.say("Kicking failed.")
        else:
            await self.client.say("BOOM. Banned "+member.name)

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member):
        """Kicks a member from the server.
        In order to do this, the bot and you must have Kick Member permissions.
        """
        try:
            await self.client.kick(member)
        except discord.Forbidden:
            await self.client.say("The bot does not have permissions to kick members.")
        except discord.HTTPException:
            await self.client.say("Kicking failed.")
        else:
            await self.client.say("BOOM. Kicked "+member.name)

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(ban_members=True)
    async def softban(self, ctx, member : discord.Member):
        """Bans and unbans a member from the server.
        In order to do this, the bot and you must have Ban Member permissions.

        This should be used in order to kick a member from the server whilst also
        deleting all the messages that they have sent.
        """
        try:
            await self.client.ban(member)
            await self.client.unban(member.server, member)
        except discord.Forbidden:
            await self.client.say("The bot does not have permissions to kick members.")
        except discord.HTTPException:
            await self.client.say("Kicking failed.")
        else:
            await self.client.say("Softbanned "+member.name+". Their messages should be gone now.")

def setup(client):
        client.add_cog(Admin(client))
