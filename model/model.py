from __future__ import annotations

import uuid
from datetime import datetime
from mailbox import Message
from typing import List

from discord import Member, Emoji, Message, Guild, Role
from peewee import *
from playhouse.mysql_ext import JSONField

from storage.database_factory import DatabaseFactory

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
    emoji = CharField(null=True, index=True, max_length=255)

    @classmethod
    def add_or_update(cls, guild_id: int, channel_id: int, emoji: str, threshold: int):
        existing = cls.get_or_none(cls.channel_id == channel_id)

        if existing is None:
            return cls.create(guild_id=guild_id, channel_id=channel_id, emoji=emoji, threshold=threshold)

        existing.emoji = emoji
        existing.star_threshold = threshold
        existing.save()

        return existing

    @classmethod
    def get_for_guild(cls, guild_id: int, emoji: Emoji):
        select = cls.select().where((cls.guild_id == guild_id) & (cls.emoji.contains(str(emoji)))).limit(1)

        for row in select:
            return row

    class Meta:
        table_name = "discord_starboard"


class StarredMessageModel(BaseModel):
    id = AutoField(primary_key=True)
    message_id = BigIntegerField()
    message_channel_id = BigIntegerField()
    starboard = ForeignKeyField(StarboardModel, related_name="messages")
    embed_message_id = BigIntegerField(unique=True, null=True)
    datetime_added = DateTimeField()
    user_id = BigIntegerField()
    is_muted = BooleanField()

    @classmethod
    async def get_in_starboard(cls, message_id: int, starboard_id: int):
        select = cls.select().where((cls.message_id == message_id) & (cls.starboard_id == starboard_id))

        for row in select:
            return row

    @classmethod
    async def create_from_message(cls, message: Message, starboard: StarboardModel):
        return cls.create(message_id=message.id,
                          message_channel_id=message.channel.id,
                          starboard_id=starboard.id,
                          is_muted=False, datetime_added=datetime.utcnow(),
                          user_id=message.author.id)

    class Meta:
        table_name = "discord_starboard_messages"


class MessageStarrerModel(BaseModel):
    id = AutoField()
    message = ForeignKeyField(StarredMessageModel, column_name='starred_message_id', related_name="starrers")
    user_id = BigIntegerField()
    datetime_starred = DateTimeField()

    @classmethod
    async def add_starred_message(cls, message_id: int, starrer_id: int):
        MessageStarrerModel.insert(starred_message_id=message_id, user_id=starrer_id,
                                   datetime_starred=datetime.utcnow()) \
            .on_conflict(update={MessageStarrerModel.datetime_starred: datetime.utcnow()}).execute()

    @classmethod
    async def delete_starrer_message(cls, message_id: int, starrer_id: int):
        return cls.delete().where((MessageStarrerModel.starred_message_id == message_id) &
                                  (MessageStarrerModel.user_id == starrer_id)).execute()

    class Meta:
        table_name = "discord_starboard_message_starrers"


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
    def get_total_for_guild_members(cls, guild: Guild, members) -> float:
        query = (cls.select(fn.SUM(PointTransaction.amount).alias('total_points'))
                 .where((PointTransaction.guild_id == guild.id) &
                        (PointTransaction.recipient_user_id << members)))

        return query.scalar()

    @classmethod
    def get_leaderboard_for_guild(cls, guild: Guild, limit: int = 10):
        return (cls.select(PointTransaction.recipient_user_id,
                           fn.SUM(PointTransaction.amount).alias('total_points'))
                .where(PointTransaction.guild_id == guild.id)
                .group_by(PointTransaction.recipient_user_id)
                .order_by(SQL('total_points DESC'))
                .limit(limit))

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


class PointLeaderboard(BaseModel):
    id = AutoField()
    guild_id = BigIntegerField()
    name = CharField(max_length=255)

    @classmethod
    async def add_for_guild(cls, guild: Guild, leaderboard_name: str, roles: List[Role]):
        if cls.get_or_none((cls.name == leaderboard_name) & (cls.guild_id == guild.id)) is not None:
            raise IntegrityError("Guild already has a leaderboard by that name.")

        leaderboard = cls.create(guild_id=guild.id, name=leaderboard_name)

        # Add PointLeaderBoardTeam objects based on roles.
        for role in roles:
            PointLeaderboardTeam.create(leaderboard_id=leaderboard.id, discord_role_id=role.id)

        return leaderboard

    @classmethod
    async def get_for_guild(cls, guild: Guild, leaderboard_name: str):
        return cls.get_or_none((cls.name == leaderboard_name) & (cls.guild_id == guild.id))

    class Meta:
        table_name = "discord_point_leaderboards"


class PointLeaderboardTeam(BaseModel):
    id = AutoField()
    leaderboard_id = ForeignKeyField(PointLeaderboard, related_name="teams")
    discord_role_id = BigIntegerField()

    class Meta:
        table_name = "discord_point_leaderboard_teams"


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
