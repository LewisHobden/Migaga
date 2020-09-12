import configparser

import discord
from playhouse.migrate import MySQLMigrator, migrate

from model.model import *

factory = DatabaseFactory()
database = factory.get_database_connection()

migrator = MySQLMigrator(database)

# migrate(
#     migrator.add_column('discord_guild_configs', 'starboard_emoji_id', BigIntegerField(null=True)),
# )

# Load the config
config = configparser.ConfigParser()
config.read("config.ini")

# Set up the bot.
client = discord.Client()


@client.event
async def on_ready():
    for guild in client.guilds:
        config = await GuildConfig.get_for_guild(guild.id)

        server_logs = discord.utils.get(guild.channels, name='server-logs')

        if server_logs is not None:
            config.server_logs_channel_id = server_logs.id
            config.save()

            await server_logs.send("I've been updated! If you're interested check out my changelog: https://github.com/LewisHobden/Migaga/blob/master/CHANGELOG.md")
        # If this update required action from the server, we could send them a message here.

    await client.close()


client.run(config.get("Env", "Token"))
