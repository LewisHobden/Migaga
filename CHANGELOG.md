# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
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