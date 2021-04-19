import configparser

import discord
from playhouse.migrate import MySQLMigrator, migrate

from model.model import *

factory = DatabaseFactory()
database = factory.get_database_connection()

migrator = MySQLMigrator(database)

database.create_tables([
    PointLeaderboard,
    PointLeaderboardTeam
])
