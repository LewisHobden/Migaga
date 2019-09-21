from peewee import *
from model.reminder import Reminder
from storage.database_factory import DatabaseFactory


class ReminderDestination(Model):
    id = AutoField()
    reminder = ForeignKeyField(Reminder, backref="destinations")
    destination_type = CharField()
    destination_id = BigIntegerField()

    class Meta:
        table_name = "discord_reminder_destinations"

        factory = DatabaseFactory()
        database = factory.get_database_connection()
