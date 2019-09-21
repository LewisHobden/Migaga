from peewee import *
from storage.database_factory import DatabaseFactory


class StarboardModel(Model):
    id = AutoField()
    guild_id = BigIntegerField(unique=True)
    channel_id = BigIntegerField(unique=True)
    is_locked = BooleanField()

    @classmethod
    def get_for_guild(cls, guild_id: int):
        select = cls.select().where(cls.guild_id == guild_id).limit(1)

        for row in select:
            return row
    
    class Meta:
        table_name = "discord_starboard"

        factory = DatabaseFactory()
        database = factory.get_database_connection()
