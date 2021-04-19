import configparser

import discord
from playhouse.migrate import MySQLMigrator, migrate

from model.model import *

factory = DatabaseFactory()
database = factory.get_database_connection()

migrator = MySQLMigrator(database)


with database.atomic() as transaction:
    database.create_tables([
        ServerLogChannel,
        ServerLogChannelEvent
    ])

    for config in GuildConfig.select().where(GuildConfig.server_logs_channel_id != None):
        ServerLogChannel.add_for_channel(config.server_logs_channel_id)

    migrate(
        migrator.drop_column('discord_guild_configs', 'server_logs_channel_id'),
    )
