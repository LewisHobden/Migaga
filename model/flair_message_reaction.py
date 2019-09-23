from peewee import *
from storage.database_factory import DatabaseFactory
import uuid


def _generate_reference():
    return str(uuid.uuid4())[:8]


class FlairMessageReactionModel(Model):
    reference = CharField(max_length=8, primary_key=True)
    discord_message_id = BigIntegerField()
    emoji_id = BigIntegerField()
    role_id = BigIntegerField()

    class Meta:
        table_name = "discord_flair_message_reactions"

        factory = DatabaseFactory()
        database = factory.get_database_connection()

    @classmethod
    def generate_unique_reference(cls):
        id = _generate_reference()

        try:
            while True:
                cls.get_by_id(id)
                id = _generate_reference()
        except DoesNotExist:
            return id
