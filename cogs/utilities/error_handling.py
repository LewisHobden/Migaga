import logging

from discord.ext import commands
import discord
import sys
import datetime


class ErrorHandling(commands.Cog):
    """The main error handler."""

    def __init__(self, client: commands.Bot):
        self.client = client
        client.add_listener(self._report_error, "on_command_error")

    async def _report_error(self, ctx, exception):
        if type(exception) in [commands.CommandNotFound]:
            return

        if type(exception) is commands.MissingRequiredArgument or type(exception) is commands.MissingPermissions:
            await ctx.send(str(exception) +
                           "\nUse `!help <command>` for more information on the command you were trying to call.")

            return

        if type(exception) is commands.BadArgument:
            await ctx.send("You called this command incorrectly. Don't forget that more than one word for a command "
                           "argument should be wrapped in quotes. Here's the error message I got back: \n" + str(
                            exception))

        logger = logging.getLogger('discord')
        logger.error(exception)

        # Otherwise report it to my tracebacks channel.
        exceptions_channel = discord.utils.get(self.client.get_guild(197972184466063381).channels,
                                               id=254215930416988170)

        msg = discord.Embed(title=str(type(exception)), timestamp=datetime.datetime.utcnow(), description=str(exception),
                            color=discord.Colour(15021879))

        msg.add_field(name="Command", value=ctx.command.qualified_name)
        msg.add_field(name="Server", value=ctx.guild.name)
        msg.add_field(name="Channel", value=ctx.channel.name)
        msg.set_footer(text=str(sys.stderr))
        msg.set_author(name=str(ctx.author.name), icon_url=ctx.author.avatar_url)

        await exceptions_channel.send(embed=msg)


def setup(client):
    client.add_cog(ErrorHandling(client))
