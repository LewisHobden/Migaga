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

    @commands.command(name="roll", aliases=["dice", "throw"])
    async def _roll(self, ctx, dice: str):
        """ Ask the bot to roll a dice, try "D20" or "40". """
        dice_type = int(dice.replace("d", ""))

        if dice_type < 2 or dice_type > 100000:
            return await ctx.send("I don't really recognise that kind of dice.")

        await ctx.send("You rolled a **{}**!".format(random.randint(0, dice_type)))

    @commands.command(name="rollmultiple", aliases=["multidice", "multiroll"])
    async def _roll_multiple(self, ctx, number_of_dice: int, dice: str):
        """ Ask the bot to roll a dice a number of times, try "3 D20" or "4 40". """
        dice_type = int(dice.replace("d", ""))
        rolls = []

        if dice_type < 2 or dice_type > 100000:
            return await ctx.send("I don't really recognise that kind of dice.")

        if number_of_dice > 500:
            return await ctx.send("I can't roll that many dice!")

        for i in range(1, number_of_dice):
            rolls.append(random.randint(0, dice_type))

        total_dice_formatted = "`{}`\n = ".format(" + ".join(map(str, rolls)))

        if len(total_dice_formatted) > 1950:
            total_dice_formatted = ""

        await ctx.send("You rolled\n{}**{}**!".format(total_dice_formatted, sum(rolls)))

    @commands.command()
    async def kitten(self, ctx):
        """ Random kitten pictures! So sweet. """
        url = "http://www.randomkittengenerator.com/cats/rotator.php"
        file = discord.File(await _get_remote_file(url), filename="kitten.jpg")

        await ctx.send("Here you are!", file=file)

    @commands.Cog.listener('on_message')
    async def dair(self, msg):
        """ Updates bottom message of a specific channel """
        if msg.channel.id != 740191241349890168:
            return

        if msg.author == self.client.user:
            return

        if self.botDair is not None:
            await self.botDair.delete()

        emoji = self.client.get_emoji(741072210713903206)
        self.botDair = await msg.channel.send(str(emoji))


def setup(client):
    client.add_cog(Fun(client))
