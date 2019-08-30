from discord.ext import commands

import discord
import datetime

import os


async def _generate_boilerplate_embed(author: discord.Member, colour=None, channel: discord.TextChannel = None):
    e = discord.Embed()

    if colour is not None:
        e.colour = discord.Colour(colour)

    if channel is not None:
        e.add_field(name="Channel Name:", value=channel.name)
        e.add_field(name="Channel Link:", value=channel.mention)

    e.set_author(name=author.display_name, icon_url=author.avatar_url)
    e.timestamp = datetime.datetime.now()

    return e


async def _get_roles_as_text(roles):
    formatted_roles = []

    for role in roles:
        formatted_roles.append(role.name.replace("@", "[at]"))

    return ', '.join(formatted_roles)


class ServerLogs(commands.Cog):
    """ Logging server activity. """

    def __init__(self, client):
        self.client = client
        client.add_listener(self._on_message_delete, "on_message_delete")
        client.add_listener(self._on_message_edit, "on_message_edit")
        client.add_listener(self._on_member_join, "on_member_join")
        client.add_listener(self._on_member_leave, "on_member_leave")
        client.add_listener(self._on_member_banned, "on_member_ban")
        client.add_listener(self._on_member_unbanned, "on_member_unban")
        client.add_listener(self._on_member_updated, "on_member_update")
        client.add_listener(self._on_user_updated, "on_user_update")

    async def _on_member_leave(self, member: discord.Member):
        e = await _generate_boilerplate_embed(member, 9319990)
        e.title = "\N{CROSS MARK} Member Left the Server!"
        e.description = member.display_name + " has left this server. Sad to see them go! I think? I might not be.."

        e.add_field(name="Member Since:", value=member.joined_at.strftime("%d of %b %Y at\n%H:%M:%S"), inline=True)

        await self._notify(e, member.guild)

    async def _on_member_join(self, member: discord.Member):
        e = await _generate_boilerplate_embed(member, 6278268)
        e.title = "\N{CHECK MARK} User Joined the Server!"

        e.description = member.display_name + " has joined the server. Welcome!"
        date_created = member.created_at.strftime("%d of %b %Y at\n%H:%M:%S")

        e.add_field(name="User Since:", value=date_created, inline=True)
        e.add_field(name="Clickable:", value=member.mention, inline=True)

        await self._notify(e, member.guild)

    async def _on_member_unbanned(self, user: discord.User):
        e = await _generate_boilerplate_embed(user, 1219369)
        e.title = "\N{LOW BRIGHTNESS SYMBOL} Member Unbanned"
        e.description = user.display_name + " was unbanned from the server. I hope they learned their lesson!"

        await self._notify(e, kwargs.get("guild"))

    async def _on_member_banned(self, user: discord.User):
        e = await _generate_boilerplate_embed(user, 10162706)
        e.title = "\N{NAME BADGE} User Banned"
        e.description = user.name + " was banned from this server. Lay down the law!"

        await self._notify(e, kwargs.get("guild"))

    async def _on_message_delete(self, message: discord.Message):
        e = await _generate_boilerplate_embed(message.author, 11346466, message.channel)

        e.title = "\N{CROSS MARK} Message Deleted"
        e.description = message.content if message.content else "_No message._"

        if message.attachments:
            # Save and post each attachment.
            for attachment in message.attachments:
                filename = "tmp/downloaded-images/" + attachment.filename
                await attachment.save(filename, use_cached=True)

                e.set_image(url=await self._save_file_to_cdn(filename))

        await self._notify(e, message.channel.guild)

    async def _on_message_edit(self, message_before: discord.Message, message_after: discord.Message):
        if message_before.content == message_after.content:
            return

        e = await _generate_boilerplate_embed(message_after.author, 16235052)
        e.title = "\N{WARNING SIGN} Message Edit"

        e.add_field(name="Before", value=message_before.clean_content)
        e.add_field(name="After", value=message_after.clean_content)
        e.description = "[Click here](" + message_after.jump_url + ") to jump to the message."

        await self._notify(e, message_after.channel.guild)

    async def _on_user_updated(self, before: discord.User, after: discord.User):
        e = await _generate_boilerplate_embed(after, 7748003)
        e.title = "\N{LOWER RIGHT PENCIL} User Changed"

        if before.name != after.name:
            e.add_field(name="Username Before", value=before.name)
            e.add_field(name="Username After", value=after.name)

        if before.discriminator != after.discriminator:
            e.add_field(name="Discriminator Before", value=before.discriminator)
            e.add_field(name="Discriminator After", value=after.discriminator)

        if before.avatar != after.avatar:
            e.description = "Avatar has changed."
            image_format = "gif" if before.is_avatar_animated() else "png"

            before_avatar_path = "tmp/downloaded-avatars/" + str(after.id) + "." + image_format
            await before.avatar_url_as(format=image_format).save(before_avatar_path)

            e.set_image(url=await self._save_file_to_cdn(before_avatar_path))
            e.set_thumbnail(url=after.avatar_url)

        for guild in self.client.guilds:
            member = discord.utils.find(lambda m: m.id == after.id, guild.members)

            if member is not None:
                await self._notify(e, guild)

    async def _on_member_updated(self, before: discord.Member, after: discord.Member):
        needs_posting = False

        e = await _generate_boilerplate_embed(after, 7748003)
        e.title = "\N{LOWER RIGHT PENCIL} Member Changed"

        if before.nick != after.nick:
            needs_posting = True
            e.add_field(name="Nickname Before", value=before.nick if before.nick else "_No Nickname_")
            e.add_field(name="Nickname After", value=after.nick if after.nick else "_No Nickname_")

        if before.roles != after.roles:
            needs_posting = True
            e.add_field(name="Roles Before", value=await _get_roles_as_text(before.roles))
            e.add_field(name="Roles After", value=await _get_roles_as_text(after.roles))

        if needs_posting:
            await self._notify(e, after.guild)

    # @todo Refactor this to not use hard-coded values. Possibly a different approach?
    async def _save_file_to_cdn(self, filename: str) -> str:
        guild = discord.utils.find(lambda c: c.id == 197972184466063381, self.client.guilds)
        cdn = discord.utils.find(lambda c: c.name == "cdn", guild.channels)

        message = await cdn.send(file=discord.File(open(filename, "rb")))
        url = message.attachments[0].url

        os.remove(filename)

        return url

    async def _notify(self, embed: discord.Embed, guild: discord.Guild):
        server_logs = discord.utils.get(guild.channels, name='server-logs')

        await server_logs.send(embed=embed)


def setup(client):
    client.add_cog(ServerLogs(client))
