from cogs.customcommands import *
import configparser
import discord
import datetime

# Load the config
config = configparser.ConfigParser()
config.read("config.ini")

# Set up the bot.
bot_description = """ Lewis' Discord Bot Version 4 """
prefix = "!"
client = commands.Bot(command_prefix=prefix, description=bot_description, pm_help=None)

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

    await client.change_presence(status=discord.Status.online, activity=discord.Activity(name="I'm updated!"))


if __name__ == '__main__':
    token = config.get("Env", "Token")
    client.client_id = "309765060908285952"

    for extension in extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    client.run(token)
