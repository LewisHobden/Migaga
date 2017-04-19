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
        
        if event_name == 'MESSAGE_REACTION_ADD' or event_name == 'MESSAGE_REACTION_REMOVE':
            if payload['emoji']['name'] != "⭐":
                return
            
            channel = self.client.get_channel(payload.get('channel_id'))
            
            if channel is None or channel.is_private:
                return

            # Check if this message has already been starred.
            server = channel.server
            db = self.stars.get(server.id)
            message = await self.client.get_message(channel, payload['message_id'])
            member  = message.author

            if event_name == 'MESSAGE_REACTION_ADD':
                data = await self.starMessage(message,db)
            else:
                data = await self.unstarMessage(message,db)

            if None == data:
                await self.stars.remove(message.id)
            else:
                await self.stars.put(message.id, data)
            
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
            everyone = discord.PermissionOverwrite(read_messages=True, send_messages=False, read_message_history=True,add_reactions=False)
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

    async def createEmbedForStarredMessage(self,message,db):        
        e = discord.Embed()
        e.timestamp = message.timestamp
        author = message.author

        avatar = author.default_avatar_url if not author.avatar else author.avatar_url
        avatar = avatar.replace('.gif', '.jpg')
        e.set_author(name=author.display_name, icon_url=avatar)

        e.description = message.content
        e.timestamp   = message.timestamp

        message_data = db['messages'][message.id]
        number_of_stars = len(message_data['starred_user_ids'])
        star_emoji      = await self.getEmojiForStar(number_of_stars)   

        e.add_field(name="Stars",value=star_emoji+" **"+str(number_of_stars)+"**")
        return e

    async def starMessage(self,message,db):
        starboard = self.client.get_channel(db.get('channel'))
        
        if message.id in db['messages']:
            message_data = db['messages'][message.id]
            print(message_data)
            bot_message = await self.client.get_message(starboard,message_data['bot_message_id'])
            db['messages'][message.id]['starred_user_ids'].append(message.author.id)
        else:
            bot_message = await self.client.send_message(starboard, "In <#"+message.channel.id+">")
            db['messages'][message.id] = {"bot_message_id" : bot_message.id, "starred_user_ids" : [message.author.id]}
            message_data = db['messages'][message.id]

        await self.client.edit_message(bot_message, embed=await self.createEmbedForStarredMessage(message,db))
                           
        return message_data

    async def unstarMessage(self,message,db):
        starboard = self.client.get_channel(db.get('channel'))
        
        message_data = db['messages'][message.id]
        bot_message = await self.client.get_message(starboard,message_data['bot_message_id'])
        db['messages'][message.id]['starred_user_ids'].remove(message.author.id)

        if len(db['messages'][message.id]['starred_user_ids']) == 0:
            await self.client.delete_message(bot_message)
            return None

        await self.client.edit_message(bot_message, "In <#"+message.channel.id+">",embed=await self.createEmbedForStarredMessage(message,db))

        return message_data


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
