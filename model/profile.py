from peewee import *
from storage.database_factory import DatabaseFactory


class ProfileModel(Model):
    discord_user_id = BigIntegerField(primary_key=True)
    colour = IntegerField()
    tag = CharField(max_length=256)
    bio = CharField(max_length=2048)

    class Meta:
        table_name = "discord_profiles"

        factory = DatabaseFactory()
        database = factory.get_database_connection()
