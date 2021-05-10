from playhouse.migrate import MySQLMigrator, migrate

from model.model import *

factory = DatabaseFactory()
database = factory.get_database_connection()

migrator = MySQLMigrator(database)

with database.atomic() as transaction:
    migrate(
        migrator.add_column('discord_guild_configs', 'prefix',
                            CharField(null=False, max_length=5, index=True, default="!")),
    )
