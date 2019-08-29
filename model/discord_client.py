from discord.ext import commands
import discord


class MigagaClient(commands.Bot):
    def __init__(self, **options):
        super().__init__(**options)

        self.event_listeners = {}

    async def on_message(self, message):
        if message.author == self.user:
            return

        await self._on_event("message", message=message)

    async def on_raw_reaction_add(self, data: discord.RawReactionActionEvent):
        await self._on_event("raw_reaction_add", reaction=data)

    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        await self._on_event("member_banned", guild=guild, user=user)

    async def on_member_update(self, member_before: discord.Member, member_after: discord.Member):
        await self._on_event("member_update", member_before=member_before, member_after=member_after)

    async def on_message_delete(self, message: discord.Message):
        await self._on_event("message_delete", message=message)

    async def on_message_edit(self, message_before: discord.Message, message_after: discord.Message):
        await self._on_event("message_edit", message_before=message_before, message_after=message_after)

    async def on_member_join(self, member: discord.Member):
        await self._on_event("member_join", member=member)

    async def on_member_remove(self, member: discord.Member):
        await self._on_event("member_leave", member=member)

    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        await self._on_event("member_unbanned", guild=guild, user=user)

    async def on_user_update(self, user_before: discord.User, user_after: discord.User):
        await self._on_event("user_update", user_before=user_before, user_after=user_after)

    async def on_raw_reaction_remove(self, data: discord.RawReactionActionEvent):
        await self._on_event("raw_reaction_remove", reaction=data)

    def register_event_listener(self, event_name: str, callback: callable):
        self.event_listeners.setdefault(event_name, []).append(callback)

    async def _on_event(self, event_name: str, **kwargs):
        try:
            event_listeners = self.event_listeners[event_name]
        except KeyError:
            print("No event listeners registered for "+event_name)
            return

        for callback in event_listeners:
            await callback(**kwargs)
