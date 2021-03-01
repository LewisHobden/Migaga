# Migaga (Version 4)

## What's this?
This is the repo for my passion project Discord bot. I don't know exactly how many servers it is in - nor how many users it interacts with on a regular basis. I would estimate that it's in the 1000s. It was primarily built as a helper for some of the servers I was in personally. This was before bots were as accessible as they are now, or before the mobile app was as advanced as it is currently. 
I figured I would make the source code public as exposure therapy for my fear of "imperfect" code being made public with my name against it. We're all progressing professionally and personally, chronicling that only helps accelerate the process.. I hope! 

## Background
Like many others, my first solo venture into learning programming was through writing a Discord bot while learning Python as my first language in college, 4 years ago. 
This is my longest maintained project, it certainly looks nothing like what I originally wrote, albeit a chunk of the logic has remained the same.. if only I knew about source control back then. 
It started as a 500(ish) line if statement on the "on_message" event, executing all wild and creative code I could write inside each condition. Around once a year I have done a full sweep of the code, refactoring every file.
I like to use the yearly refactor sessions as a way to monitor my progression as a developer, even if I no longer necessarily have the time to make it as "perfect" as I envision. It also has the added benefit of helping me to keep versed in Python, since professionally I have no interaction with the language.
It used to be running on an old Windows laptop in the corner of my bedroom that I'd restart manually multiple times a day, I shifted it a year later onto a Raspberry Pi. From there it has lived on a Windows VM in AWS, a (significantly cheaper) Linux instance in Linode and now onto a containerised app. From a large text file for storage (seriously) to JSON, from JSON to MySQL, from MySQL to an ORM.

Thanks for reading!

## Architecture
- Running on Python 3.9 on Docker.
- Stores data on a MySQL 8.0 database.

To get started contributing, copy `example_config.ini` to `config.ini` and update the ClientId or 