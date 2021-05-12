from discord.ext.commands import Bot


class Migaga(Bot):
    async def process_commands(self, message):
        if message.author.bot and not (str(message.author.id) in self.whitelisted_bot_ids):
            return

        ctx = await super().get_context(message)
        await super().invoke(ctx)
