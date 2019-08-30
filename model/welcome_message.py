from peewee import *
from storage.database_factory import DatabaseFactory


class WelcomeMessage(Model):
    id = AutoField()
    message = CharField(max_length=2000)
    server_id = BigIntegerField()
    channel_id = BigIntegerField()

    class Meta:
        table_name = "discord_welcome_messages"

        factory = DatabaseFactory()
        database = factory.get_database_connection()
