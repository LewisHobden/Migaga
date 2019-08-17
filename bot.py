from discord.ext import commands

from cogs.utilities.error_handling import ErrorHandling
from cogs.customcommands import CustomCommands
from cogs.admin import Admin
from cogs.games.currency import connectToDatabase
from cogs.storage.database import Database
from time import gmtime, strftime

import configparser

import discord
import datetime
import logging
import sys
import traceback


most_recent_name_change = None

# Load the config
config = configparser.ConfigParser()
config.read("config.ini")

# Begin logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='migagalogs.logger', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot_description = """ Lewis' Discord Bot Version 4 """
prefix          = "!"
client          = commands.Bot(command_prefix=prefix, description=bot_description, pm_help=None)

debug = False

extensions = [
                "cogs.smash.smash",
                "cogs.admin",
                "cogs.games.currency",
                "cogs.games.games",
                "cogs.customcommands",
                "cogs.games.fun",
                "cogs.people",
                "cogs.starboard",
                "cogs.serverlogs",
                "cogs.games.quiz",
                "cogs.utilities.get_messages",
            ]

@client.event
async def on_command_error(error, ctx):
    exceptions_channel = discord.utils.get(client.get_all_channels(), guild__id='197972184466063381', id='254215930416988170')

    if debug == True:
        exceptions_channel = ctx.message.channel

    if isinstance(error, commands.DisabledCommand):
        await client.send_message(ctx.message.author, 'This command has been disabled for now.')
    if isinstance(error, commands.NoPrivateMessage):
        await client.send_message(ctx.message.author, 'You will have to do this command in a server, not PMs sorry!')
    elif isinstance(error, commands.CommandInvokeError):
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
    print('------')
    if not hasattr(client, 'uptime'):
        client.uptime = datetime.datetime.utcnow()

    await client.change_presence(activity=discord.Activity(name="In charge of sacred object",type=1,url='http://shulk101.com/'))

    await CustomCommands.readCommands(CustomCommands)

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='server-logs')
    logs    = client.get_cog('ServerLogs')
    e       = await logs.showMemberJoin(member)

    if None != e and None != channel:
        await client.send_message(channel, embed=e)

    connection = connectToDatabase()
    with connection.cursor() as cursor:
        sql = "SELECT `message`,`channel_id` FROM `discord_welcome_messages` WHERE `server_id`=%s"
        cursor.execute(sql, member.guild.id)
        result = cursor.fetchone()

    if None == result:
        return

    channel = client.get_channel(str(result['channel_id']))

    if None == channel:
        raise Exception

    await client.send_message(channel,result['message'].format(member.mention,member.display_name,member.guild.name))

@client.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.channels, name='server-logs')
    logs    = client.get_cog('ServerLogs')
    e       = await logs.showMemberLeave(member)

    if None != e and None != channel:
        await client.send_message(channel, embed=e)

@client.event
async def on_member_update(member_before,member_after):
    global most_recent_name_change

    channel = discord.utils.get(member_after.guild.channels, name='server-logs')
    logs    = client.get_cog('ServerLogs')
    e = await logs.determineUserChange(member_before,member_after)

    database = Database()

    if member_before.name != member_after.name and None != most_recent_name_change and member_after.id != most_recent_name_change.id and member_after.name != most_recent_name_change.name:
        database.query("INSERT INTO `discord_username_changes` VALUES(0,%s,%s,%s)",[member_after.name,member_after.id,strftime("%Y-%m-%d %H:%M:%S", gmtime())])

    most_recent_name_change = member_after

    if None != e and None != channel:
        await client.send_message(channel, embed=e)

@client.event
async def on_message_edit(message_before,message_after):
    channel = discord.utils.get(message_after.server.channels, name='server-logs')
    logs    = client.get_cog('ServerLogs')
    e = await logs.showMessageEdit(message_before,message_after)

    if None != e and None != channel:
        await client.send_message(channel, embed=e)

@client.event
async def on_member_ban(member):
    channel = discord.utils.get(member.guild.channels, name='server-logs')
    logs    = client.get_cog('ServerLogs')
    e       = await logs.showMemberBan(member)

    if None != e and None != channel:
        await client.send_message(channel, embed=e)

@client.event
async def on_member_unban(server,user):
    channel = discord.utils.get(server.channels, name='server-logs')
    logs    = client.get_cog('ServerLogs')
    e       = await logs.showMemberUnban(user)

    if None != e and None != channel:
        await client.send_message(channel, embed=e)

@client.event
async def on_message_delete(message):
    channel = discord.utils.get(message.server.channels, name='server-logs')
    logs    = client.get_cog('ServerLogs')
    e       = await logs.showMessageDelete(message)

    if None != e and None != channel:
        await client.send_message(channel, embed=e)

@client.event
async def on_command(command, ctx):
    message = ctx.message
    destination = None
    if message.channel.is_private:
        destination = 'Private Message'
    else:
        destination = '#s{0.channel.name} - {0.server.name}'.format(message)

    logger.info('{0.timestamp}: {0.author.name} in {1}: {0.content}'.format(message, destination))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(prefix):
        admin = client.get_cog('Admin')

        space_location = message.content.find(" ")
        if space_location == -1:
            command = message.content[1:]
        else:
            command = message.content[1:space_location]

        if admin:
            if await admin.checkAndAssignRole(command,message):
                return

        response = await CustomCommands.checkIfCommandTriggered(CustomCommands,message,command)

        if response != False:
            await client.send_message(message.channel,response)
        else:
            await client.process_commands(message)

if __name__ == '__main__':
    token            = config.get("Env","Token")
    client.client_id = "309765060908285952"

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
