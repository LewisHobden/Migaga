from discord.ext import commands
import random
import discord

import requests
import io


async def _get_remote_file(url):
    response = requests.get(url)

    return io.BytesIO(response.content)


class Fun(commands.Cog):
    """ Silly, assorted commands. """

    def __init__(self, client):
        self.client = client
        self.botDair = None

    @commands.command()
    async def emoji(self, ctx, emoji: discord.Emoji):
        """ Loads the full version of an emoji as long as you give one that is in this server! """
        fp = io.BytesIO()
        await emoji.url.save(fp=fp)

        filename = "emoji." + ("gif" if emoji.animated else "png")

        await ctx.send("Here's the full version of the emoji {}".format(emoji.name),
                       file=discord.File(fp=fp, filename=filename))

    @commands.command()
    async def choose(self, ctx, *, message: str):
        """ Choose between things (separate with a comma) """
        choices = message.split(",")

        await ctx.send("Alright. I choose.. \n:speech_balloon: **{}**".format(random.choice(choices).strip()))

    @commands.command()
    async def cat(self, ctx):
        """ Type this to get a cute picture of a cat! """
        api_url = "http://aws.random.cat/meow"
        image_url = requests.get(api_url).json()

        file = discord.File(await _get_remote_file(image_url['file']), filename="cat.jpg")
        await ctx.send("Here you are!", file=file)

    @commands.command()
    async def dog(self, ctx):
        """ Random dog pictures! So sweet. """
        url = "http://www.randomdoggiegenerator.com/randomdoggie.php"
        file = discord.File(await _get_remote_file(url), filename="puppy.jpg")

        await ctx.send("Here you are!", file=file)

    @commands.command()
    async def kitten(self, ctx):
        """ Random kitten pictures! So sweet. """
        url = "http://www.randomkittengenerator.com/cats/rotator.php"
        file = discord.File(await _get_remote_file(url), filename="kitten.jpg")

        await ctx.send("Here you are!", file=file)

    @commands.Cog.listener('on_message')
    async def dair(self, msg):
        """ Updates bottom message of a specific channel """
        if msg.channel.id == 740191241349890168:
            if msg.author != self.client.user:
                if self.botDair is not None:
                    await self.botDair.delete()
                self.botDair = await msg.channel.send(":Shulk_Dair4:")

def setup(client):
    client.add_cog(Fun(client))
