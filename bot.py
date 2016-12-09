from discord.ext import commands

from cogs.utilities.error_handling import ErrorHandling
from cogs.customcommands import CustomCommands

import discord
import datetime
import logging
import sys
import traceback


# Begin logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='migagalogs.logger', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot_description = """ Lewis' Discord Bot Version 3 """
prefix          = "-"
client          = commands.Bot(command_prefix=prefix, description=bot_description, pm_help=None)

extensions = ["cogs.admin", "cogs.games.currency", "cogs.games.games", "cogs.customcommands", "cogs.games.fun"]

@client.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.DisabledCommand):
        await client.send_message(ctx.message.author, 'This command has been disabled for now.')
    if isinstance(error, commands.NoPrivateMessage):
        await client.send_message(ctx.message.author, 'You will have to do this command in a server, not PMs sorry!')
    elif isinstance(error, commands.CommandInvokeError):
        exceptions_channel = discord.utils.get(client.get_all_channels(), server__id='197972184466063381', id='254215930416988170')
        
        msg = discord.Embed(title="CommandInvokeError", timestamp=datetime.datetime.utcnow(), description=str(error), color=discord.Colour(15021879))
        msg.add_field(name="Command", value=ctx.command.qualified_name)
        msg.add_field(name="Server", value=ctx.message.server.name)
        msg.add_field(name="Channel", value=ctx.message.channel.name)
        try:
            msg.add_field(name="Location", value=str(traceback.format_tb(error.original.__traceback__)[1]))
        except:
            msg.add_field(name="Location", value=str(traceback.format_tb(error.original.__traceback__)))

        msg.set_footer(text=str(sys.stderr), icon_url="https://cdn0.iconfinder.com/data/icons/shift-free/32/Error-128.png")

        member = ctx.message.author
        avatar = member.avatar_url if member.avatar else member.default_avatar_url
        msg.set_author(name=str(member), icon_url=avatar)

        await client.send_message(exceptions_channel, embed=msg)


@client.event
async def on_ready():
    print('Logged in as: '+client.user.name)
    print('ID: '+client.user.id)
    print('------')
    if not hasattr(client, 'uptime'):
        client.uptime = datetime.datetime.utcnow()

    await CustomCommands.readCommands(CustomCommands)

@client.event
async def on_command(command, ctx):
    #increment commands used in db

    message = ctx.message
    destination = None
    if message.channel.is_private:
        destination = 'Private Message'
    else:
        destination = '#{0.channel.name} - {0.server.name}'.format(message)

    logger.info('{0.timestamp}: {0.author.name} in {1}: {0.content}'.format(message, destination))
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith(prefix):
        response = await CustomCommands.checkIfCommandTriggered(CustomCommands, message)
        
        if response != False:
            await client.send_message(message.channel, response)
            
            
    await client.process_commands(message)

if __name__ == '__main__':
    token            = "MTk3OTg3Nzk0NDA3MTI5MDg5.CyG-Wg.pbAtNfwpI0WNqOzU7rQvhGDaJLE"
    client.client_id = "197987769732038656"

    for extension in extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    client.run(token)
    handlers = logger.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        logger.removeHandler(hdlr)
    
