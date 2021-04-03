from __future__ import annotations

from datetime import datetime
from discord import Member
from peewee import *
from playhouse.mysql_ext import JSONField

from storage.database_factory import DatabaseFactory
import uuid

factory = DatabaseFactory()
database = factory.get_database_connection()


def _generate_reference():
    return str(uuid.uuid4())[:8]


class BaseModel(Model):
    class Meta:
        database = database


class CustomCommand(BaseModel):
    id = AutoField()
    name = CharField(max_length=255)
    description = TextField()
    response = TextField()
    server_id = BigIntegerField()

    @classmethod
    def get_possible_commands_by_name(cls, guild_id: int, command: str) -> iter:
        return cls.select(cls.name) \
            .where((cls.name.contains(command)) & (cls.server_id == guild_id)) \
            .order_by(cls.name) \
            .group_by(cls.name)

    @classmethod
    def get_random_response_by_name(cls, guild_id: int, command: str) -> iter:
        data = cls.select(cls.response).where((cls.name == command) & (cls.server_id == guild_id)) \
            .order_by(fn.rand()) \
            .limit(1)

        for command in data:
            return command.response

    @classmethod
    def get_responses_by_name(cls, guild_id: int, command: str):
        return cls.select(cls.id, cls.name, cls.response, cls.description) \
            .where((cls.name.contains(command)) & (cls.server_id == guild_id)) \
            .order_by(cls.name)

    class Meta:
        table_name = "discord_commands"


class FlairMessageReactionModel(BaseModel):
    reference = CharField(max_length=8, primary_key=True)
    discord_message_id = BigIntegerField()
    emoji_id = BigIntegerField()
    role_id = BigIntegerField()

    class Meta:
        table_name = "discord_flair_message_reactions"

    @classmethod
    def generate_unique_reference(cls):
        id = _generate_reference()

        try:
            while True:
                cls.get_by_id(id)
                id = _generate_reference()
        except DoesNotExist:
            return id


class StarboardModel(BaseModel):
    id = AutoField()
    guild_id = BigIntegerField()
    channel_id = BigIntegerField(unique=True)
    is_locked = BooleanField()
    star_threshold = IntegerField(default=1)
    emoji_id = CharField(null=True, index=True, max_length=255)

    @classmethod
    def get_for_guild(cls, guild_id: int):
        select = cls.select().where(cls.guild_id == guild_id).limit(1)

        for row in select:
            return row

    class Meta:
        table_name = "discord_starboard"


class StarredMessageModel(BaseModel):
    message_id = BigIntegerField(unique=True, primary_key=True)
    message_channel_id = BigIntegerField()
    starboard = ForeignKeyField(StarboardModel, related_name="messages")
    embed_message_id = BigIntegerField(unique=True, null=True)
    datetime_added = DateTimeField()
    user_id = BigIntegerField()
    is_muted = BooleanField()

    class Meta:
        table_name = "discord_starboard_messages"


class MessageStarrerModel(BaseModel):
    id = AutoField()
    message = ForeignKeyField(StarredMessageModel, related_name="starrers")
    user_id = BigIntegerField()
    datetime_starred = DateTimeField()

    class Meta:
        table_name = "discord_starboard_message_starrers"

        indexes = (
            (("user_id", "message"), True),
        )


class ProfileModel(BaseModel):
    discord_user_id = BigIntegerField(primary_key=True)
    colour = IntegerField()
    tag = CharField(max_length=256)
    bio = CharField(max_length=2048)

    class Meta:
        table_name = "discord_profiles"


class ProfileFieldModel(BaseModel):
    id = AutoField()
    discord_user_id = ForeignKeyField(ProfileModel, related_name="fields")
    key = CharField(max_length=255)
    value = CharField(max_length=1024)

    class Meta:
        table_name = "discord_profile_fields"

        indexes = (
            (('discord_user_id', 'key'), True),
        )


class Reminder(BaseModel):
    id = AutoField()
    creator_discord_id = BigIntegerField()
    datetime = DateTimeField()
    reminder = TextField()
    has_reminded = BooleanField()

    class Meta:
        table_name = "discord_reminders"


class ReminderDestination(BaseModel):
    id = AutoField()
    reminder = ForeignKeyField(Reminder, backref="destinations")
    destination_type = CharField()
    destination_id = BigIntegerField()

    class Meta:
        table_name = "discord_reminder_destinations"


class RoleOverwrite(BaseModel):
    id = AutoField()
    role_id = BigIntegerField()
    overwrite_role_id = BigIntegerField()
    server_id = BigIntegerField()

    class Meta:
        table_name = "discord_role_overwrites"


class GuildConfig(BaseModel):
    id = AutoField()
    guild_id = BigIntegerField()
    server_logs_channel_id = BigIntegerField(null=True)
    points_name = TextField(null=True)
    points_emoji = TextField(null=True)
    config_data = JSONField(null=True)

    @classmethod
    async def get_for_guild(cls, guild_id: int) -> GuildConfig:
        try:
            config = cls.select().where(cls.guild_id == guild_id).get()
        except DoesNotExist:
            cls.create(guild_id=guild_id).save()

            return await cls.get_for_guild(guild_id=guild_id)

        return config

    class Meta:
        table_name = "discord_guild_configs"


class PointTransaction(BaseModel):
    id = AutoField()
    guild_id = BigIntegerField()
    recipient_user_id = BigIntegerField(null=True)
    sender_user_id = BigIntegerField(null=True)
    amount = DecimalField(null=True)
    timestamp = DateTimeField(default=datetime.now)

    @classmethod
    async def get_total_for_member(cls, member: Member) -> float:
        query = cls.select(fn.SUM(cls.amount)).where(
            (cls.recipient_user_id == member.id) & (cls.guild_id == member.guild.id))

        return query.scalar()

    @classmethod
    async def grant_member(cls, amount: float, member: Member, sender: Member) -> float:
        return cls.create(guild_id=member.guild.id, recipient_user_id=member.id, sender_user_id=sender.id,
                          amount=amount).save()

    @classmethod
    async def get_position_in_guild_leaderboard(cls, guild_id: int, user_id: int) -> int:
        with open("/app/storage/leaderboard_query.sql", 'r') as file:
            query = file.read()

        for row in database.execute_sql(query.format(guild_id, user_id)):
            return row

    class Meta:
        table_name = "discord_point_transactions"


class RoleAlias(BaseModel):
    id = AutoField()
    alias = CharField(max_length=100)
    role_id = BigIntegerField()
    server_id = BigIntegerField()
    is_admin_only = BooleanField()
    uses = IntegerField()

    class Meta:
        table_name = "discord_role_aliases"


class WelcomeMessage(BaseModel):
    id = AutoField()
    message = CharField(max_length=2000)
    server_id = BigIntegerField()
    channel_id = BigIntegerField()

    @classmethod
    def get_for_guild(cls, guild_id: int):
        return cls.select().where(cls.server_id == guild_id)

    class Meta:
        table_name = "discord_welcome_messages"
