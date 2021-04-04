import configparser
from playhouse.migrate import MySQLMigrator, migrate
from model.model import *

factory = DatabaseFactory()
database = factory.get_database_connection()

migrator = MySQLMigrator(database)

# Load the config
config = configparser.ConfigParser()
config.read("config.ini")

migrate(
    migrator.drop_index('discord_starboard', 'starboardmodel_guild_id'),
    migrator.add_column('discord_starboard', 'emoji_id', CharField(null=True, max_length=255, index=True)),
)

database.execute_sql(
    "UPDATE discord_starboard JOIN discord_guild_configs config ON config.`guild_id` = discord_starboard.`guild_id` "
    "SET discord_starboard.`emoji_id` = config.`starboard_emoji_id`"
)

migrate(
    migrator.drop_column('discord_guild_configs', 'starboard_emoji_id'),
    migrator.add_column('discord_guild_configs', 'config_data', JSONField(null=True)),
)
