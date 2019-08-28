from peewee import *
from storage.database_factory import DatabaseFactory
from model.starboard import StarboardModel


class StarredMessageModel(Model):
    message_id = BigIntegerField(unique=True, primary_key=True)
    starboard = ForeignKeyField(StarboardModel, related_name="messages")
    embed_message_id = BigIntegerField(unique=True, null=True)
    datetime_added = DateTimeField()
    user_id = BigIntegerField()
    is_muted = BooleanField()

    class Meta:
        table_name = "discord_starboard_messages"

        factory = DatabaseFactory()
        database = factory.get_database_connection()
