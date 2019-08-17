import discord
from discord.ext import commands

from discord.http import HTTPClient
from discord.http import Route

class GetMessages(commands.Cog):
    """ Util for getting messages."""
    def __init__(self, client):
        self.client = client

    def getMessages(self,channel_id,limit):
        r = Route('GET', '/channels/{channel_id}/messages', channel_id=channel_id,limit=limit)
        return HTTPClient.request(self.client.http,r)

def setup(client):
    client.add_cog(GetMessages(client))
