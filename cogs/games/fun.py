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

    @commands.command(pass_context=True)
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

    @commands.command(pass_context=True)
    async def dog(self, ctx):
        """ Random dog pictures! So sweet. """
        url = "http://www.randomdoggiegenerator.com/randomdoggie.php"
        file = discord.File(await _get_remote_file(url), filename="puppy.jpg")

        await ctx.send("Here you are!", file=file)

    @commands.command(pass_context=True)
    async def kitten(self, ctx):
        """ Random kitten pictures! So sweet. """
        url = "http://www.randomkittengenerator.com/cats/rotator.php"
        file = discord.File(await _get_remote_file(url), filename="kitten.jpg")

        await ctx.send("Here you are!", file=file)


def setup(client):
    client.add_cog(Fun(client))
