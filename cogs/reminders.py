from discord.ext import commands, tasks
import discord
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
from model.reminder import Reminder
from model.reminder_destination import ReminderDestination


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


class Reminders(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.format = "%H:%M on %m %B %Y"

        self.reminder.start()

    @commands.command(pass_context=True)
    async def remind(self, ctx, destination: DestinationConverter, hours: int, minutes: int, *, reminder):
        """ Set up a reminder from the bot. The destination could either be a user by tag, yourself "me" or a channel.
        There are a few different ways to set up a reminder. This one uses hours, minutes and seconds specifically. """
        now = datetime.utcnow()
        delta = timedelta(hours=hours, minutes=minutes)
        reminder_time = now + delta

        await _queue_reminder(ctx.author, destination, reminder_time, reminder)

        await ctx.send("Ok! {.mention} will get the reminder \"{}\" at {}".format(destination, reminder,
                                                                                  reminder_time.strftime(self.format)))

    @commands.command(pass_context=True)
    async def reminddate(self, ctx, destination: DestinationConverter, date: DateConverter, *, reminder):
        """ Set up a reminder from bot. The destination could either be a user by tag, yourself "me" or a channel.
        There are a few different ways to set up a reminder. This one uses a date. Don't forget that if you're . """
        await ctx.send("Ok! {.mention} will get the reminder \"{}\" at {}".format(destination, reminder,
                                                                                  date.strftime(self.format)))

    @tasks.loop(minutes=1.0)
    async def reminder(self):
        queued_reminders = Reminder.select()\
            .where((Reminder.datetime <= datetime.utcnow()) & (Reminder.has_reminded == False))

        for reminder in queued_reminders:
            for destination in reminder.destinations:
                if destination.destination_type == "<class 'discord.member.Member'>":
                    destination = self.client.get_user(destination.destination_id)
                elif destination.destination_type == "<class 'discord.channel.TextChannel'>":
                    destination = self.client.get_channel(destination.destination_id)
                else:
                    raise LookupError("Bad data type in the database.")

                await destination.send("Reminder: "+reminder.reminder)

            reminder.has_reminded = True
            reminder.save()

    @reminder.before_loop
    async def before_reminders(self):
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(Reminders(client))
