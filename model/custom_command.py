from peewee import *
from storage.database_factory import DatabaseFactory


class CustomCommand(Model):
    id = AutoField()
    name = CharField(max_length=255)
    description = TextField()
    response = TextField()
    server_id = BigIntegerField()

    @classmethod
    def get_random_response_by_name(cls, command: str) -> iter:
        data = cls.select(cls.response).where(cls.name == command).order_by(fn.rand()).limit(1)

        for command in data:
            return command.response

    @classmethod
    def get_responses_by_name(cls, command: str):
        data = cls.select(cls.response).where(cls.name == command).order_by(fn.rand()).limit(1)

    class Meta:
        table_name = "discord_commands"

        factory = DatabaseFactory()
        database = factory.get_database_connection()
