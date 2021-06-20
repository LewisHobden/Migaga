from model.model import *

factory = DatabaseFactory()
connection = factory.get_database_connection()

connection.create_tables([
    BoosterMessage,
    BoosterRoleConfig,
    BoosterRole,
])