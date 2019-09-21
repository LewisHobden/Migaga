from peewee import *
from storage.database_factory import DatabaseFactory
from model.profile import ProfileModel


class ProfileFieldModel(Model):
    id = AutoField()
    discord_user_id = ForeignKeyField(ProfileModel, related_name="fields")
    key = CharField(max_length=255)
    value = CharField(max_length=1024)

    class Meta:
        table_name = "discord_profile_fields"

        indexes = (
            (('discord_user_id', 'key'), True),
        )

        factory = DatabaseFactory()
        database = factory.get_database_connection()
