from model.model import *

factory = DatabaseFactory()
connection = factory.get_database_connection()

connection.create_tables([
    CustomCommand,
    MessageStarrerModel,
    ProfileModel,
    ProfileFieldModel,
    Reminder,
    ReminderDestination,
    RoleAlias,
    RoleOverwrite,
    StarboardModel,
    StarredMessageModel,
    WelcomeMessage,
    FlairMessageReactionModel
])
