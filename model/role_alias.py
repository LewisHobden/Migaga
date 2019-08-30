from peewee import *
from storage.database_factory import DatabaseFactory


class RoleAlias(Model):
    id = AutoField()
    alias = CharField(max_length=100)
    role_id = BigIntegerField()
    server_id = BigIntegerField()
    is_admin_only = BooleanField()
    uses = IntegerField()

    class Meta:
        table_name = "discord_role_aliases"

        factory = DatabaseFactory()
        database = factory.get_database_connection()
