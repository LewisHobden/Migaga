from peewee import *
from storage.database_factory import DatabaseFactory


class RoleOverwrite(Model):
    id = AutoField()
    role_id = BigIntegerField()
    overwrite_role_id = BigIntegerField()
    server_id = BigIntegerField()

    class Meta:
        table_name = "discord_role_overwrites"

        factory = DatabaseFactory()
        database = factory.get_database_connection()
