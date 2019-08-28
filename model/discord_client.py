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
