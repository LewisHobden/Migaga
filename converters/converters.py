import discord
from discord.ext import commands
from discord.ext.commands import BadArgument, UserConverter, PartialEmojiConversionFailure
import re
from emoji import UNICODE_EMOJI_ENGLISH

from model.model import GuildConfig


class GlobalUserConverter(commands.IDConverter):
    async def convert(self, ctx, argument):
        bot = ctx.bot
        user = None
        member_converter = UserConverter()

        try:
            user = await member_converter.convert(ctx=ctx, argument=argument)
        except BadArgument:
            match = self._get_id_match(argument) or re.match(r'<@!?([0-9]+)>$', argument)

            try:
                if match is not None:
                    user = await bot.fetch_user(argument)

            except discord.NotFound:
                raise BadArgument('User "{}" not found'.format(argument))

        if user is None:
            raise BadArgument('User "{}" not found'.format(argument))

        return user


class GuildConfigConverter(commands.Converter):
    async def convert(self, ctx, argument):
        return await GuildConfig.get_for_guild(ctx.guild.id)


class PartialEmojiWithUnicodeConverter(commands.PartialEmojiConverter):
    async def convert(self, ctx, argument):
        try:
            return await super().convert(ctx, argument)
        except PartialEmojiConversionFailure:
            if argument in UNICODE_EMOJI_ENGLISH:
                return argument

        raise PartialEmojiConversionFailure(argument)
