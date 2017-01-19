from discord.ext import commands
from .utilities import credential_checks, config

import discord
import datetime
import asyncio
import logging
import random
import time
import re
import json

def load_starboard():
    def load(ctx):
        ctx.guild_id = ctx.message.server.id
        ctx.db = ctx.cog.stars.get(ctx.guild_id, {})
        ctx.starboard = ctx.bot.get_channel(ctx.db.get('channel'))
        if ctx.starboard is None:
            raise StarError('\N{WARNING SIGN} Starboard channel not found.')
        return True

    return commands.check(load)

class Starboard:
    """ Commands related to the Starboard. """
    def __init__(self, client):
        self.client = client

        # config format:
        # <guild_id> : as follows ->
        # channel: <starboard channel id>
        # locked: <boolean indicating locked status>
        # messages : as follows ->
        # message_id: as follows ->
        # bot_message: <bot message>
        # starred_user_ids : [<starred user ids>]
        self.stars = config.Config('stars.json')

        # cache message objects.
        self._message_cache = {}
        

    async def on_socket_raw_receive(self, data):
        # no binary allowed please
        if isinstance(data, bytes):
            return

        data       = json.loads(data)
        event_name = data.get('t')
        payload    = data.get('d')
        
        if event_name == 'MESSAGE_REACTION_ADD':
            if payload['emoji']['name'] != "⭐":
                return
            
            channel = self.client.get_channel(payload.get('channel_id'))
            
            if channel is None or channel.is_private:
                return

            # Check if this message has already been starred.
            server = channel.server
            db = self.stars.get(server.id)
            starboard = self.client.get_channel(db.get('channel'))
            message = await self.client.get_message(channel, payload['message_id'])
            member = channel.server.get_member(payload['user_id'])

            
            if message.id in db['messages']:
                message_data = db['messages'][message.id]
                message_data['starred_user_ids'].append(member.id)

                number_of_stars = len(message_data['starred_user_ids'])
                star_emoji      = await self.getEmojiForStar(number_of_stars)
                                                        
                bot_message = message_data['bot_message']
                await self.client.edit_message(bot_message, star_emoji+" - "+str(number_of_stars))
            else:
                bot_message = await self.client.send_message(starboard, embed=await self.createEmbedForStarredMessage(message))
                db['messages'][message.id] = {"bot_message" : bot_message, "starred_user_ids" : [member.id]}
            
            if member is None or member.bot:
                return

            if db is None:
                return

    @commands.command(pass_context=True, no_pm=True)
    @credential_checks.hasPermissions(administrator=True)
    async def starboard(self, ctx, *, name: str = 'starboard'):
        """Sets up the starboard for this server.
        This creates a new channel with the specified name
        and makes it into the server's "starboard". If no
        name is passed in then it defaults to "starboard".
        
        If the channel is deleted then the starboard is
        deleted as well.
        
        You must have Administrator permissions to use this
        command.
        """
        server = ctx.message.server
        stars = self.stars.get(server.id, {})
        
        previous_starboard = self.client.get_channel(stars.get('channel'))
        if previous_starboard is not None:
            fmt = 'This server already has a starboard ({.mention})'
            await self.client.say(fmt.format(previous_starboard))
            return

        # Just make sure all old data is deleted.
        stars = {}

        bot_permissions = ctx.message.channel.permissions_for(server.me)
        args = [server, name]

        # Make sure that people cannot send messages in the starboard.
        if bot_permissions.manage_roles:
            mine = discord.PermissionOverwrite(send_messages=True, manage_messages=True, embed_links=True)
            everyone = discord.PermissionOverwrite(read_messages=True, send_messages=False, read_message_history=True)
            args.append((server.me, mine))
            args.append((server.default_role, everyone))

        try:
            channel = await self.client.create_channel(*args)
        except discord.Forbidden:
            await self.client.say('I do not have permissions to create a channel.')
        except discord.HTTPException:
            await self.client.say('This channel name is bad or an unknown error happened.')
        else:
            stars['channel']  = channel.id
            stars['locked']   = False
            stars['messages'] = {}
            await self.stars.put(server.id, stars)
            await self.client.say('\N{GLOWING STAR} Starboard created at ' + channel.mention)

    async def createEmbedForStarredMessage(self,message):
        e = discord.Embed()
        e.timestamp = message.timestamp
        author = message.author

        avatar = author.default_avatar_url if not author.avatar else author.avatar_url
        avatar = avatar.replace('.gif', '.jpg')
        e.set_author(name=author.display_name, icon_url=avatar)

        e.title = "Message Starred"
        e.description = message.content
        e.timestamp   = message.timestamp

        return e


    async def getEmojiForStar(self,stars):
        if 5 >= stars >= 0:
            return '\N{WHITE MEDIUM STAR}'
        elif 10 >= stars >= 6:
            return '\N{GLOWING STAR}'
        elif 25 >= stars >= 11:
            return '\N{DIZZY SYMBOL}'
        else:
            return '\N{SPARKLES}'

def setup(client):
    client.add_cog(Starboard(client))
