from discord.ext.commands import MinimalHelpCommand
from discord_slash import SlashCommand

from cogs.customcommands import *
import configparser
import discord

import logging

# Load the config
config = configparser.ConfigParser()
config.read("config.ini")

# Set up the bot.
version = config.get("Env", "Version")
bot_description = "Migaga {}".format(version)
prefix = "!"
client = commands.Bot(command_prefix=prefix, description=bot_description, intents=discord.Intents.all(), pm_help=None,
                      activity=discord.Game(name="{}!".format(version)))
slash = SlashCommand(client, override_type=True, application_id=int(config.get("Env", "ClientId")))

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
    # await slash.sync_all_commands()


if __name__ == '__main__':
    token = config.get("Env", "Token")

    for extension in extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    client.help_command = MinimalHelpCommand()
    client.run(token)
