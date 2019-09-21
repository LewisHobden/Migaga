from peewee import *
from storage.database_factory import DatabaseFactory


class Reminder(Model):
    id = AutoField()
    creator_discord_id = BigIntegerField()
    datetime = DateTimeField()
    reminder = TextField()
    has_reminded = BooleanField()

    class Meta:
        table_name = "discord_reminders"

        factory = DatabaseFactory()
        database = factory.get_database_connection()
