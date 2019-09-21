from peewee import *
from storage.database_factory import DatabaseFactory
from model.starred_message import StarredMessageModel


class MessageStarrerModel(Model):
    id = AutoField()
    message = ForeignKeyField(StarredMessageModel, related_name="starrers")
    user_id = BigIntegerField()
    datetime_starred = DateTimeField()
    
    class Meta:
        table_name = "discord_starboard_message_starrers"

        factory = DatabaseFactory()
        database = factory.get_database_connection()
        indexes = (
            (("user_id", "message"), True),
        )
