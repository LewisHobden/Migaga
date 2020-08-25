from playhouse.migrate import MySQLMigrator, migrate

from model.model import *

factory = DatabaseFactory()
database = factory.get_database_connection()

migrator = MySQLMigrator(database)

migrate(
    migrator.add_column('discord_guild_configs', 'starboard_emoji_id', BigIntegerField(null=True)),
)

# # Load the config
# config = configparser.ConfigParser()
# config.read("config.ini")
#
# # Set up the bot.
# client = discord.Client()
#
#
# @client.event
# async def on_ready():
#     message = "Hi! I'm contacting you because you own a server I'm in. " \
#               "I've been updated and this means some things may be broken. " \
#               "Not sure what yet."
#
#     for guild in client.guilds:
#         await guild.owner.send(message)
#
#     await client.close()


# client.run(config.get("Env", "Token"))