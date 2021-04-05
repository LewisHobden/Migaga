import configparser
from playhouse.migrate import MySQLMigrator, migrate
from model.model import *

factory = DatabaseFactory()
database = factory.get_database_connection()

migrator = MySQLMigrator(database)

# Load the config
config = configparser.ConfigParser()
config.read("config.ini")

with database.atomic() as transaction:
    migrate(
        migrator.drop_index('discord_starboard', 'starboardmodel_guild_id'),
        migrator.add_column('discord_starboard', 'emoji', CharField(null=True, max_length=255, index=True)),
    )

    migrate(
        migrator.drop_foreign_key_constraint('discord_starboard_message_starrers', 'message_id'),
        migrator.drop_index('discord_starboard_messages', 'PRIMARY'),
        migrator.add_column('discord_starboard_messages', 'id', AutoField(primary_key=True, null=True)),
        migrator.add_column('discord_starboard_message_starrers', 'starred_message_id', ForeignKeyField(StarredMessageModel, null=True, field=StarredMessageModel.id)),
    )

    database.execute_sql(
        "UPDATE discord_starboard_message_starrers starrers "
        "JOIN discord_starboard_messages messages ON messages.`message_id` = starrers.`message_id` "
        "SET starrers.`starred_message_id` = messages.`id`"
    )

    migrate(
        migrator.drop_index('discord_starboard_message_starrers', 'messagestarrermodel_user_id_message_id'),
        migrator.drop_index('discord_starboard_message_starrers', 'messagestarrermodel_message_id'),
        migrator.drop_column('discord_starboard_message_starrers', 'message_id'),
    )

    database.execute_sql(
        "UPDATE discord_starboard "
        "JOIN discord_guild_configs config ON config.`guild_id` = discord_starboard.`guild_id` "
        "SET discord_starboard.`emoji_id` = config.`starboard_emoji_id`"
    )

    migrate(
        migrator.drop_column('discord_guild_configs', 'starboard_emoji_id'),
        migrator.add_column('discord_guild_configs', 'config_data', JSONField(null=True)),
    )