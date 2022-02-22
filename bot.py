from discord.ext.commands import MinimalHelpCommand, Bot
from discord_slash import SlashCommand

from cogs.customcommands import *
import configparser
import discord

import logging

from model.bot import Migaga


async def prefix(bot: Bot, message: Message):
    guild_config = await GuildConfig.get_for_guild(message.guild.id)

    return guild_config.prefix


# Load the config
config = configparser.ConfigParser()
config.read("config.ini")

# Set up the bot.
version = config.get("Env", "Version")
bot_description = "Migaga {}".format(version)
intents = discord.Intents.default()
intents.members = True
intents.messages = True

client = Migaga(command_prefix=prefix, description=bot_description, intents=intents, pm_help=None,
                activity=discord.Game(name="{}!".format(version)))
slash = SlashCommand(client, override_type=True, application_id=int(config.get("Env", "ClientId")))

logging.basicConfig(level=logging.INFO)

# Get our cogs.
extensions = [
    "cogs.admin",
    "cogs.booster",
    "cogs.config",
    "cogs.games.games",
    "cogs.customcommands",
    "cogs.message_events",
    "cogs.profile",
    "cogs.games.fun",
    "cogs.people",
    "cogs.points",
    "cogs.starboard",
    "cogs.serverlogs",
    "cogs.reminders",
    "cogs.utilities.error_handling",
    "cogs.games.dice",
]


@client.event
async def on_ready():
    print('Logged in as: ' + client.user.name)
    print('------')

    setattr(client, "client_id", config.get("Env", "ClientId"))
    setattr(client, "whitelisted_bot_ids", config.get("Bot", "WhitelistedBotIds").split(" "))

    await slash.sync_all_commands()

if __name__ == '__main__':
    token = config.get("Env", "Token")

    for extension in extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    client.help_command = MinimalHelpCommand()
    client.run(token)
