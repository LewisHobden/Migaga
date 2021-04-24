from playhouse.migrate import MySQLMigrator

from model.model import *

factory = DatabaseFactory()
database = factory.get_database_connection()

migrator = MySQLMigrator(database)

database.create_tables([MemberWarning])
