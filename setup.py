from model.model import *

# Create tables. That's it for now.. Database versioning would be nice.
# @todo Send messages to server owners to let them know of an update.
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
