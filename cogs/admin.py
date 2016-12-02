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
    @credential_checks.hasPermissions(kick_members=True)
    async def kick(self, member : discord.Member):
        """Kicks a member from the server.
        In order for this to work, the bot must have Kick Member permissions.
        To use this command you must have Kick Members permission or have the
        Bot Admin role.
        """

        try:
            await self.client.kick(member)
        except discord.Forbidden:
            await self.client.say('The bot does not have permissions to kick members.')
        except discord.HTTPException:
            await self.client.say('Kicking failed.')
        else:
            await self.client.say('\U0001f44c')

def setup(client):
    client.add_cog(Admin(client))
