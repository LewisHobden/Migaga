import configparser

import discord
from playhouse.migrate import MySQLMigrator, migrate
from playhouse.mysql_ext import JSONField

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

migrate(
    migrator.drop_index('discord_starboard', 'starboardmodel_guild_id'),
    migrator.add_column('discord_starboard', 'emoji_id', CharField(null=True, max_length=255, index=True)),
    migrator.drop_column('discord_guild_configs', 'starboard_emoji_id'),
    migrator.add_column('discord_guild_configs', 'config_data', JSONField(null=True)),
)
