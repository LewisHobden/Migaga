from cogs.customcommands import *
import configparser
import discord
import datetime

most_recent_name_change = None

# Load the config
config = configparser.ConfigParser()
config.read("config.ini")

# Set up the bot.
bot_description = """ Lewis' Discord Bot Version 4 """
prefix = "!"
client = commands.Bot(command_prefix=prefix, description=bot_description, pm_help=None)

debug = False

# Get our cogs.
extensions = [
    "cogs.admin",
    "cogs.games.games",
    "cogs.customcommands",
    "cogs.profile",
    "cogs.games.fun",
    "cogs.people",
    "cogs.starboard",
    "cogs.serverlogs",
    "cogs.reminders",
    "cogs.utilities.error_handling",
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
