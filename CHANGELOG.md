# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [4.10.2] - 2022-02-22
### Tweaks
- Lowered number of Discord intents requested.

## [4.10.1] - 2021-06-21
### Booster Features
- Booster roles are now automatically removed and deleted when a user no longer boosts the server.
- Fixed a bug with the importer.

## [4.10.0] - 2021-06-21
### Booster Features
- You can now configure messages to be posted when a person newly boosts a server. 
- You can now enable booster roles for your server - allowing users who boost the server to assign themselves roles.
- Users can edit the name and the colour for these booster roles.
- If your server already uses booster roles, you can import them into Migaga to work instantly.

### Tweaks
- Fixed the default number of dice when rolling without specifying a number of dice.
- The ID of the user who caused an action is now included in server logs.

## [4.9.3] - 2021-06-17
### Features
- Added a few more features to the dice rolling commands.
- You can now request Migaga send a message when banning a user. 

## [4.9.2] - 2021-05-29
### Features
- Added some functions for rolling dice.

### Tweaks
- Fixed an issue that would cause starred messages to persist if the original message was deleted.

## [4.9.1] - 2021-05-12
### Tweaks
- Fixed a rendering issue when displaying starboard messages with an image and no content.
- Updated bot whitelisting to apply to all commands.
- Tweaked server logs to reduce some bloat in logs.

## [4.9.0] - 2021-05-10
### Features
- Migaga now supports custom prefixes!

### Tweaks
- When requesting an inventory for somebody without points, a message is now sent.
- When using `!addrole` the prefix is automatically removed to avoid double prefix requirements.
- Point commands can now be triggered by whitelisted bots.

## [4.8.3] - 2021-05-07
### Fixes
- Squished some bugs.

## [4.8.2] - 2021-04-25
### Fixes
- Fixed some errors in the logs.

## [4.8.1] - 2021-04-25
### Features
- Updated the `!invite` command to also ask for slash commands permissions.
- Reinstated the log channel server, lost to the annals of git.

## [4.8.0] - 2021-04-25
### Slash Commands
- Starboards can now be configured using slash commands. The original way of adding starboards has been removed.
- Server configuration can be modified using slash commands.

### Features
- Servers can now have more than one starboard. 
- Custom starboard emoji can now also include the default Discord unicode emoji.
- Greatly streamlined the starboard process.

### Warnings
- Server admins can now add warnings to people in their server.
- Warnings can be viewed using a slash command.

### Maintenance
- Banning confirmation now ignore the case of the response.
- Version number is now automatically picked up in the CI process.

## [4.7.4] - 2021-03-31
### Tweaks
- Required confirmation before banning users. 
- Removed the delete_message_days parameter when banning users. 

### Maintenance
- Only run Docker releases when a new release has been pushed.
- Started preparations for using Slash Commands.

## [4.7.3] - 2021-03-18
### Features
- When a message is starred that is a reply to another message, a summary of the message is included in the starboard post.
- Improved the layout of a starboard message.

### Fixes
- Fixed a bug that would cause some valid `!remindme` messages to fail validation.  

## [4.7.2] - 2021-03-02
### Tweaks
- Fixed an issue where leaderboard position would be incorrectly displayed when requesting another user's inventory.
- Added an updated total display when a user gifts points to another user.

## [4.7.1] - 2021-03-01
### Tweaks
- Updated the Readme to be a bit more helpful for new people.
- Fixed a permissions issue reading the leaderboard query.

## [4.7.0] - 2021-03-01
### Features
- Updated the `!inventory` command to include the user's position on the leaderboard.
- Users can now gift points to other members of their guild.

### Tweaks
- Ensured that the response message when running `!points add [negative value]` is correct, and the same for taking.
- Aliased "add, remove" for points assigning.

### Maintenance
- Updated Python version to 3.9.

## [4.6.1] - 2021-02-03
### Fixes
- The leaderboard now only shows the top 5 users by points.
- Fixed dev configuration being put on live.

## [4.6.0] - 2021-02-03
### Features
- Added a !leaderboard command to show users with the most points in a guild. 
  
### Tweaks
- Updated discord.py version.
- Tweaked points formatting.

### Fixes
- Fixed requests to Discord intents.
- Fixed a crash when cleaning the Starboard and finding deleted messages.

## [4.5.1] - 2020-09-12
### Fixes
- Tweaked GitHub actions.
- Changed the emoji sent into the #long-dair channel.

## [4.5.0] - 2020-09-12
### Features
- The !ban command will now check users globally by ID.

### Server Config
Introducing configuration options so that a server can have more control over how the bot works. 
Use !help config to get started.
- Server logs no longer write logs to whatever channel it finds named #server-logs. The channel must now be configured.
- Starboard emoji can now be configured using the server configuration. 
- Points name and points emoji have been moved to the server config.

## [4.4.1] - 2020-08-22
### Features
- Added some aliases to the `search` command and expanded its use to allow showing all custom commands. 
- Added a `!massban` command for admins which will also search for users based on the ID.
- Added some requested aliases to common admin commands.

### Maintenance
- The bot is now running on Docker in production.

## [4.4.0] - 2020-08-08
### Points
- Added a configurable way for guild owners to add or remove points from members of their guild.
- Users can see their own or others points. 
- Points can be given a configurable name and emoji.

### Maintenance
- Improved logging for reminders and the starboard.
- Reduced the amount of time a starboard message is "cleaned up" for.

## [4.3.1] - 2020-07-27
### Maintenance
- Added logging configuration to source control. 
- Added deployment ecosystem for pm2.

## [4.3.0] - 2020-07-26
### Features
- Changed the display of the help command.
- Re-introduced the "remindme" command.

### Fixes
- Fixed a bug that would stop starboard processing for older messages.

## [4.2.0] - 2020-07-25
### Features
- Welcome messages can now be deleted from servers.
- Changed the look and feel of starboard messages. 
- Servers can now set thresholds for starred messages that will have them swept from the channel.

## [4.1.1] - 2019-10-01
### Fixes
- Added error reporting for when the user calls a command they don't have permissions for.
- Fixed a bug which caused the reminder date to be formatted incorrectly when confirming reminders.

### Database
- Refactored the database connection so that it keeps itself alive. 

## [4.1.0] - 2019-09-23
### Role Flairing
- Provided admin commands for adding and removing role flairs from a message.
- When a user reacts to a message configured with a role flair they will be given the roles recorded against that message.
- If a role has overwrites set up against it then the other roles will be removed when reacting.
- Added helper commands for finding information on reaction flairs.

### Commands
- Added a new command for removing fields from your profile.

### Fixes
- Fixed a bug which caused the removal of stars to be missed by the bot.
- Fixed a bug in the !invite command.

### Tweaks
- Changed the way database connections are managed in the event that the connection is dropped.

## [4.0.1] - 2019-09-21
### Features
- Now actually assign and remove roles based on the `!addrole` and `!overwrite` commands on message.
- Added the `!emoji` command to get a larger version of an emoji. 
- Removed the need to save changed avatars and icons to local storage.
- Changed the formatting on the Starboard.

## [4.0.0] - 2019-09-21
### Global
- Cleaned up the code a lot - you should see some performance improvements.
- With cleaner code comes greater extendability so features can be released quicker.
- Updated to use Discord.py API latest (v1.2.3).
- Updated to Python 3.7.
- Moved to a GCP database.
- Improved error reporting to the user.
- Improved command error reporting to me. 
- Removed the original logging implementation. 

### Server Logs
- Redesigned the majority of server log messages.
- Added logging for deleted images.
- Added logging for avatar changes.
 
### Games & Fun
- Removed money from games. This may be replaced in the future! Just not now.
- Fixed crashes on some games.
- Fixed a bug which would cause the choose command to give a malformed response when separating with spaces.
- Fixed the cat command!

### Starboard
- Users can no longer star themselves.
- Changed the look and feel of Starboard messages,

### Admin
- Admin commands now resolve users through ID, name, etc.
- A guild can now have multiple welcome messages.
- Fixed role overwrites.

### Profiles
- The bot now supports configured profiles with custom fields.
- Added more helpful documentation on command usage.

### Reminders
- Added a new command for making reminders in the future based on a date.
- Added the ability to remind channels and users rather than posting in the original channel.
- Reminders are now more robust. They can be queued and sent when the bot reconnects.