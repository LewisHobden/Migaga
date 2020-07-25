from discord.ext.commands import MinimalHelpCommand

from cogs.customcommands import *
import configparser
import discord

# Load the config
config = configparser.ConfigParser()
config.read("config.ini")

# Set up the bot.
version = "4.2.0"
bot_description = "Migaga (Version {})".format(version)
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

    setattr(client, "client_id", config.get("Env", "ClientId"))

    activity = "Version {}! Changelog: migaga.lewis.coffee/".format(version)
    res = await client.change_presence(status=discord.Status.online, activity=discord.Game(name=activity))


if __name__ == '__main__':
    token = config.get("Env", "Token")

    for extension in extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    client.help_command = MinimalHelpCommand()
    client.run(token)
