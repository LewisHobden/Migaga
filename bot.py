from discord.ext.commands import MinimalHelpCommand

from cogs.customcommands import *
import configparser
import discord

import logging

# Load the config
config = configparser.ConfigParser()
config.read("config.ini")

# Set up the bot.
version = "4.7.2"
bot_description = "Migaga (Version {})".format(version)
prefix = "!"
client = commands.Bot(command_prefix=prefix, description=bot_description, intents=discord.Intents.all(), pm_help=None)
logging.basicConfig(level=logging.INFO)

# Get our cogs.
extensions = [
    "cogs.admin",
    "cogs.config",
    "cogs.games.games",
    "cogs.customcommands",
    "cogs.profile",
    "cogs.games.fun",
    "cogs.people",
    "cogs.points",
    "cogs.starboard",
    "cogs.serverlogs",
    "cogs.reminders",
    "cogs.utilities.error_handling",
]


@client.event
async def on_ready():
    print('Logged in as: ' + client.user.name)
    print('------')

    setattr(client, "client_id", config.get("Env", "ClientId"))

    activity = "Version {}!".format(version)
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name=activity))


if __name__ == '__main__':
    token = config.get("Env", "Token")

    for extension in extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    client.help_command = MinimalHelpCommand()
    client.run(token)
