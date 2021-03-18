import logging
import re
from datetime import timedelta

import discord
from dateutil.parser import parse
from discord.ext import commands, tasks

from model.model import *

logger = logging.getLogger('discord')


class DateConverter(commands.Converter):
    async def convert(self, ctx, argument) -> datetime:
        try:
            return parse(argument)
        except ValueError as e:
            raise commands.BadArgument("Sorry! I couldn't understand {} as a date.".format(argument))


class DestinationConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if argument == "me":
            return ctx.author

        try:
            converter = commands.MemberConverter()
            return await converter.convert(ctx, argument)

        except commands.BadArgument:
            pass

        converter = commands.TextChannelConverter()
        return await converter.convert(ctx, argument)


async def _queue_reminder(creator: discord.Member, destination, date_time: datetime, reminder: str):
    reminder = Reminder.create(creator_discord_id=creator.id, datetime=date_time, reminder=reminder, has_reminded=False)
    destination = ReminderDestination.create(reminder=reminder, destination_type=type(destination),
                                             destination_id=destination.id)


def _parse_time_phrase_result(phrase) -> int:
    if phrase is None:
        return 0

    return int(phrase.group(0))


class Reminders(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.format = "%H:%M on %d %B %Y UTC"

        self.reminder.start()

    @commands.command()
    async def remind(self, ctx, destination: DestinationConverter, hours: int, minutes: int, *, reminder):
        """ Set up a reminder from the bot. The destination could either be a user by tag, yourself "me" or a channel.
        There are a few different ways to set up a reminder. This one uses hours, minutes and seconds specifically. """
        now = datetime.utcnow()
        delta = timedelta(hours=hours, minutes=minutes)
        reminder_time = now + delta

        await _queue_reminder(ctx.author, destination, reminder_time, reminder)

        await ctx.send("Ok! {.mention} will get the reminder \"{}\" at {}".format(destination, reminder,
                                                                                  reminder_time.strftime(self.format)))

    @commands.command()
    async def reminddate(self, ctx, destination: DestinationConverter, date: DateConverter, *, reminder):
        """ Set up a reminder from bot. The destination could either be a user by tag, yourself "me" or a channel.
        There are a few different ways to set up a reminder. This one uses a date. Don't forget that if you're . """
        await ctx.send("Ok! {.mention} will get the reminder \"{}\" at {}".format(destination, reminder,
                                                                                  date.strftime(self.format)))

    @commands.command()
    async def remindme(self, ctx, *, instruction):
        """
        A recreation of an old command. Ask the bot to remind you of something using this format:

        remindme X units to [insert message here]

        For example:
        remindme in 3 hours and 2 minutes to submit a reminder again.

        The "to" is very important!
        Your options for units are days, hours and minutes.
        """
        to_position = instruction.lower().find("to")
        error = "I don't understand! Example usage: \"!remindme in 3 hours and 2 minutes **to** submit a reminder\""

        if to_position == -1:
            return await ctx.send(error)

        reminder = instruction[to_position:]
        time_phrases = instruction[:to_position]

        if len(reminder) == 0 or len(time_phrases) == 0:
            return await ctx.send(error)

        # Match any digits that are followed by an optional space and "hour" or "minute"
        days = _parse_time_phrase_result(re.search(r'\d+(?= *day)', time_phrases))
        hours = _parse_time_phrase_result(re.search(r'\d+(?= *hour)', time_phrases))
        minutes = _parse_time_phrase_result(re.search(r'\d+(?= *minute)', time_phrases))

        hours += days * 24

        if 0 == (hours + minutes):
            return await ctx.send(error)

        return await self.remind(ctx=ctx, destination=ctx.author, hours=hours, minutes=minutes, reminder=reminder)

    @tasks.loop(minutes=1.0)
    async def reminder(self):
        queued_reminders = Reminder.select() \
            .where((Reminder.datetime <= datetime.utcnow()) & (Reminder.has_reminded == 0))

        logger.debug("Starting reminder process: {} reminders to send.".format(len(queued_reminders)))

        for reminder in queued_reminders:
            for destination in reminder.destinations:
                if destination.destination_type == "<class 'discord.member.Member'>" or destination.destination_type == "<class 'discord.member.User'>":
                    destination = self.client.get_user(destination.destination_id)
                elif destination.destination_type == "<class 'discord.channel.TextChannel'>":
                    destination = self.client.get_channel(destination.destination_id)
                else:
                    raise LookupError("Bad data type in the database.")

                await destination.send("Reminder: " + reminder.reminder)

            reminder.has_reminded = True
            reminder.save()

        logger.debug("Finishing reminder process.")

    @reminder.before_loop
    async def before_reminders(self):
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(Reminders(client))
