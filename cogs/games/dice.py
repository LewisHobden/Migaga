from random import randint

from discord.ext import commands
from discord.ext.commands import Greedy, BadArgument


class DiceConverter(commands.Converter):
    async def convert(self, ctx, argument: str):
        dice_components = argument.lower().split("d")

        if len(dice_components) != 2:
            raise KeyError("Unknown dice input: {}".format(argument))

        total_requested = dice_components[0] if dice_components[0].isnumeric() and int(dice_components[0]) > 0 else 0
        dice_figure = dice_components[1] if dice_components[1].isnumeric() and int(dice_components[1]) > 0 else 0

        return [Dice(total_sides=dice_figure) for _ in total_requested]


class KeepConverter(commands.Converter):
    async def convert(self, ctx, argument: str):
        keep = argument.lower()
        number_to_keep = argument.replace("k", "").replace("l", "")

        if not keep:
            return None

        # The keep string should either be empty, or "kl|k" followed by a number.
        if not keep.startswith("kl") or not keep.startswith("k"):
            raise BadArgument("Unknown \"keep\" argument: {}".format(keep))

        if not number_to_keep.isnumeric():
            raise BadArgument("Couldn't understand the number of dice to keep: {}".format(number_to_keep))

        return {"lowest": keep.startswith("kl"), "number_to_keep": int(number_to_keep)}


class Dice:
    def __init__(self, total_sides: int):
        self._total_sides = total_sides
        self._roll_value = None

    def roll(self) -> int:
        if self._roll_value is None:
            self._roll_value = randint(1, self._total_sides)

        return self._roll_value


class DiceCog(commands.Cog, name="Dice"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="roll", aliases=["dice"])
    async def _roll(self, ctx, dice: Greedy[DiceConverter], keep: KeepConverter = None):
        """ Ask the bot to roll a dice a number of times, try "3 D20" or "4 40". """
        index = 0

        for die_list in dice:
            for die in die_list:
                await ctx.send("rolling a dice.. {}".format(die.roll()))

        # if dice_type < 2 or dice_type > 100000:
        #     return await ctx.send("I don't really recognise that kind of dice.")
        #
        # if number_of_dice > 500:
        #     return await ctx.send("I can't roll that many dice!")
        #
        # for i in range(1, number_of_dice):
        #     rolls.append(random.randint(0, dice_type))
        #
        # total_dice_formatted = "`{}`\n = ".format(" + ".join(map(str, rolls)))
        #
        # if len(total_dice_formatted) > 1950:
        #     total_dice_formatted = ""
        #
        # await ctx.send("You rolled\n{}**{}**!".format(total_dice_formatted, sum(rolls)))


def setup(client):
    client.add_cog(DiceCog(client))
