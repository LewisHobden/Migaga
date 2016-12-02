from discord.ext import commands
import discord
import datetime

class ErrorHandling:
    """Tools for handling errors."""

    def __init__(self, client):
        self.client = client
        
    async def postErrorToChannel(ctx, error_description, error_title):
        exceptions_channel = discord.utils.get(self.client.get_all_channels(), server__id='197972184466063381', id='254215930416988170')
        
        msg  = discord.Embed(title=error_title, timestamp=datetime.datetime.utcnow(), description=error_description, color=discord.Colour(15021879))
        msg.add_field(name="Command", value=ctx.command.qualified_name)
        msg.add_field(name="Server", value=ctx.message.server.name)
        msg.add_field(name="Channel", value=ctx.message.channel.name)
        msg.set_footer(text=str(sys.stderr), icon_url="https://cdn0.iconfinder.com/data/icons/shift-free/32/Error-128.png")

        member = ctx.message.author
        avatar = member.avatar_url if member.avatar else member.default_avatar_url
        msg.set_author(name=str(member), icon_url=avatar)

        await self.client.send_message(exceptions_channel, embed=msg)

def setup(client):
    client.add_cog(ErrorHandling(client))
