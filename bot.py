from model.discord_client import MigagaClient

from cogs.customcommands import *
from cogs.storage.database import Database
from time import gmtime, strftime

import configparser

import discord
import datetime
import logging

most_recent_name_change = None

# Load the config
config = configparser.ConfigParser()
config.read("config.ini")

database = Database()

# Begin logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='migagalogs.logger', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot_description = """ Lewis' Discord Bot Version 4 """
prefix = "!"
client = MigagaClient(command_prefix=prefix, description=bot_description, pm_help=None)

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
async def on_ready():
    print('Logged in as: ' + client.user.name)
    print('------')
    if not hasattr(client, 'uptime'):
        client.uptime = datetime.datetime.utcnow()

    await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="With New Technology"))


# @client.event
# async def on_member_join(member):
#
#     sql = "SELECT `message`,`channel_id` FROM `discord_welcome_messages` WHERE `server_id`=%s"
#     cursor = database.query(sql, member.guild.id)
#     result = cursor.fetchone()
#
#     if None == result:
#         return
#
#     channel = client.get_channel(str(result['channel_id']))
#
#     if None == channel:
#         raise Exception
#
#     await client.send_message(channel, result['message'].format(member.mention, member.display_name, member.guild.name))


# @client.event
# async def on_member_update(member_before, member_after):
#     global most_recent_name_change
#
#     database = Database()
#
#     if member_before.name != member_after.name and None != most_recent_name_change and member_after.id != most_recent_name_change.id and member_after.name != most_recent_name_change.name:
#         database.query("INSERT INTO `discord_username_changes` VALUES(0,%s,%s,%s)",
#                        [member_after.name, member_after.id, strftime("%Y-%m-%d %H:%M:%S", gmtime())])
#
#     most_recent_name_change = member_after

@client.event
async def on_command(message):
    pass


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
            if await admin.checkAndAssignRole(command, message):
                return

        response = await check_if_command_triggered(message, command)

        if response != None:
            await message.channel.send(response)
        else:
            await client.process_commands(message)

if __name__ == '__main__':
    token = config.get("Env", "Token")
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
