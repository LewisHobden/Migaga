from model.custom_command import *
from model.message_starrer import *
from model.profile_field import *
from model.reminder_destination import *
from model.role_alias import *
from model.role_overwrite import *
from model.starred_message import *
from model.welcome_message import *

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
])